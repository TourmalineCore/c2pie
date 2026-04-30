from __future__ import annotations

import re
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
        tsa_url: str | None,
        require_tsa: bool,
        tsa_log_dir: str | None,
    ):
        if certificate_pem_bundle is None and certificate is not None:
            certificate_pem_bundle = certificate

        self.claim = claim
        self.private_key = private_key
        self.certificate = certificate_pem_bundle
        self.tsa_url = tsa_url
        self.require_tsa = require_tsa
        self.tsa_log_dir = tsa_log_dir

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
        """
        protected_header ; bstr

        Signing algorithms
        -7 - ES256 (ECDSA with SHA-256)
        -37 - PS256 (RSASSA-PSS с SHA-256)
        """
        protected_header: dict[int, Any] = {1: -37}  # "alg": "PS256"

        certs_in_der_format = _split_pem_certs_to_der(self.certificate or b"")
        if certs_in_der_format:
            protected_header[33] = certs_in_der_format  # 33 - is label of x5chain

        return cbor2.dumps(protected_header, canonical=True)

    def _generate_unprotected_header(self, serialized_sig_structure: bytes) -> bytes:
        """
        unprotected_header ; CBOR-map
        """
        unprotected_header: dict[str, Any] = {}

        if not self.tsa_url and self.require_tsa:
            raise TSARequiredError("Signing without a timestamp is forbidden. Provide tsa_url or set C2PIE_TSA_URL.")

        if self.tsa_url:
            time_stamp_token_der = fetch_timestamp(
                signature_bytes=serialized_sig_structure,
                tsa_url=self.tsa_url,
                tsa_log_dir=self.tsa_log_dir,
            )

            unprotected_header = {"sigTst2": {"tstTokens": [{"val": time_stamp_token_der}]}}

        return unprotected_header

    def _create_cose_sign1_tagged(self) -> bytes:
        """
        COSE_Sign1 = [
          protected_header,   ; bstr, headings that include in signature
          unprotected_header, ; CBOR-map, headings that are`t included in signature
          payload,            ; bstr, payload that will be signed (for C2PA - detached payload)
          signature           ; bstr, signature
        ]
        """
        serialized_protected_header = self._generate_protected_header()
        claim_cbor = self.claim.get_cbor_payload()

        """
        Sig_structure = [
            context,           ; string, identifier (for COSE_Sign1 - Signature1)
            protected_header,  ; bstr, headings that include a signature
            external_add,      ; bstr, external data (for C2PA - always empty)
            payload            ; bstr, payload that will be signed
        ]
        """
        sig_structure = ["Signature1", serialized_protected_header, b"", claim_cbor]
        serialized_sig_signature = cbor2.dumps(sig_structure, canonical=True)

        private_key = serialization.load_pem_private_key(self.private_key, password=None)

        signature = private_key.sign(  # type: ignore
            serialized_sig_signature,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),  # type: ignore
            hashes.SHA256(),  # type: ignore
        )

        """
        Sig_structure = [
            context,           ; string, identifier (for TSA - CounterSignature)
            protected_header,  ; bstr, headings that include a signature
            external_add,      ; bstr, external data (for C2PA - always empty)
            payload            ; bstr, payload that will be signed
        ]
        """
        tsa_sig_structure = ["CounterSignature", serialized_protected_header, b"", signature]
        serialized_tsa_sig_signature = cbor2.dumps(tsa_sig_structure, canonical=True)

        print("Hola-la-la")

        unprotected_header = self._generate_unprotected_header(serialized_sig_structure=serialized_tsa_sig_signature)

        cose_sign1 = [serialized_protected_header, unprotected_header, None, signature]

        return cbor2.dumps(cbor2.CBORTag(18, cose_sign1), canonical=True)
