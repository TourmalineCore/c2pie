from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import cbor2
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding

from c2pie.c2pa.claim import Claim
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.tsa.client import fetch_timestamp
from c2pie.tsa.exceptions import TSARequiredError
from c2pie.utils.content_types import c2pa_content_types


def _split_pem_certs_to_der(pem_bytes: bytes) -> list[bytes]:
    if not pem_bytes:
        return []

    certs = re.findall(
        b"-----BEGIN CERTIFICATE-----\\s.*?-----END CERTIFICATE-----\\s*",
        pem_bytes,
        flags=re.DOTALL,  # If remove this, the search will stop at the first \n
    )

    certs_in_der_format: list[bytes] = []

    for cert in certs:
        prepared_cert = x509.load_pem_x509_certificate(cert)
        certs_in_der_format.append(prepared_cert.public_bytes(Encoding.DER))

    return certs_in_der_format


class ClaimSignature(SuperBox):
    """
    COSE_Sign1 (PS256), detached:
      - protected: {1:-37, 33:[x5chain DER...]}
      - unprotected: {} or {"sigTst": ...} when TSA is configured
      - COSE payload = nil
      - Sig_structure payload = bstr(Claim CBOR)
    """

    def __init__(
        self,
        claim: Claim,
        *,
        private_key: bytes,
        certificate_pem_bundle: bytes = None,
        certificate: bytes = None,
        tsa_url: str | None = None,
        require_tsa: bool = False,
        tsa_log_dir: Path | str | None = None,
    ):
        if certificate_pem_bundle is None and certificate is not None:
            certificate_pem_bundle = certificate

        self.claim = claim
        self.private_key = private_key
        self.certificate = certificate_pem_bundle
        self.tsa_url = tsa_url
        self.require_tsa = require_tsa
        self.tsa_log_dir = Path(tsa_log_dir) if tsa_log_dir else None

        content_boxes = self._generate_payload()

        super().__init__(
            content_type=c2pa_content_types["claim_signature"],
            label="c2pa.signature",
            content_boxes=content_boxes,
        )

    def _generate_payload(self) -> list[ContentBox]:
        if not (self.claim and self.private_key and self.certificate):
            return []

        cose_sign1_tagged = self._create_cose_sign1_tagged()

        return [ContentBox(box_type=b"cbor".hex(), payload=cose_sign1_tagged)]

    def set_claim(self, claim: Claim):
        self.claim = claim
        content_boxes = self._generate_payload()
        super().__init__(
            content_type=c2pa_content_types["claim_signature"],
            label="c2pa.signature",
            content_boxes=content_boxes,
        )

    def _generate_protected_header(self) -> bytes:
        certs_in_der_format = _split_pem_certs_to_der(self.certificate or b"")

        # Signing algorithm
        # -7 - ES256 (ECDSA with SHA-256)
        # -37 - PS256 (RSASSA-PSS с SHA-256)
        protected: dict[int, Any] = {1: -37}  # "alg": "PS256"

        if certs_in_der_format:
            protected[33] = certs_in_der_format  # 33 - is label of x5chain

        return cbor2.dumps(protected, canonical=True)

    def _create_cose_sign1_tagged(self) -> bytes:
        """
        COSE_Sign1 = [
          protected-header,
          unprotected-header,
          payload,
          signature
        ]
        """
        serialized_protected_header = self._generate_protected_header()
        claim_cbor = self.claim.get_cbor_payload()

        """
        1 - context (for COSE_Sign1 - Signature1)
        2 - protected headers
        3 - external_add (for us - always empty)
        4 - payload (CBOR-encoded with bstr Claim)
        """
        sig_structure = ["Signature1", serialized_protected_header, b"", claim_cbor]
        tsa_sig_structure = ["CounterSignature", serialized_protected_header, b"", claim_cbor]

        serialized_sig_signature = cbor2.dumps(sig_structure, canonical=True)
        serialized_tsa_sig_signature = cbor2.dumps(tsa_sig_structure, canonical=True)

        key = serialization.load_pem_private_key(self.private_key, password=None)

        signature = key.sign(  # type: ignore
            serialized_sig_signature,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),  # type: ignore
            hashes.SHA256(),  # type: ignore
        )

        unprotected_header: dict[str, Any] = {}

        resolved_tsa_url = self.tsa_url or os.getenv("C2PIE_TSA_URL")
        resolved_require_tsa = self.require_tsa or (os.getenv("C2PIE_TSA_REQUIRED", "").lower() == "true")

        if not resolved_tsa_url and resolved_require_tsa:
            raise TSARequiredError("Signing without a timestamp is forbidden. Provide tsa_url or set C2PIE_TSA_URL.")

        if resolved_tsa_url:
            log_env = os.getenv("C2PIE_TSA_LOG_DIR")
            resolved_log_dir = self.tsa_log_dir or (Path(log_env) if log_env else None)

            time_stamp_token_der = fetch_timestamp(
                serialized_tsa_sig_signature, resolved_tsa_url, log_dir=resolved_log_dir
            )

            unprotected_header = {"sigTst": {"tstTokens": [{"val": time_stamp_token_der}]}}

        cose_sign1 = [serialized_protected_header, unprotected_header, None, signature]

        return cbor2.dumps(cbor2.CBORTag(18, cose_sign1), canonical=True)
