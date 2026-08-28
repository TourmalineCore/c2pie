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
      - unprotected: {} or {"sigTst2": ...} when TSA is configured
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

        self.serialized_cose_sign1_length = 0

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

            unprotected_header = {
                "sigTst2": {
                    "tstTokens": [
                        {
                            "val": time_stamp_token_der,
                        },
                    ],
                },
                # According to the specification, the padding size must be at least 16 bytes. 
                # However, the TSA token has a very predictable size. 
                # Therefore, the pad size has been reduced to the minimum necessary 
                # to align any possibly truncated microseconds.
                "pad": b"\x00" * 8,
            }

        return unprotected_header

    def serialize_cose_sign1_tagged_with_alignment(
        self,
        cose_sign1: list,
    ) -> bytes:
        cose_sign1_tagged_cbor = cbor2.dumps(
            cbor2.CBORTag(18, cose_sign1),
            canonical=True,
        )

        # The length of a TSA token can be variable. To ensure that a new token does not exceed
        # the exclusion boundary for the C2PA structure, we need to align the length of
        # the Claim Signature using the pad field, similar to the Data Hash Assertion.
        if self.serialized_cose_sign1_length == 0:
            self.serialized_cose_sign1_length = len(cose_sign1_tagged_cbor)
        elif self.serialized_cose_sign1_length != len(cose_sign1_tagged_cbor):
            updated_pad_length = self._calculate_updated_cose_sign1_pad_length(
                previous_pad_length=len(cose_sign1[1]["pad"]),
                previous_serialized_length=self.serialized_cose_sign1_length,
                current_serialized_length=len(cose_sign1_tagged_cbor),
            )

            cose_sign1[1]["pad"] = b"\x00" * updated_pad_length
            cose_sign1_tagged_cbor = cbor2.dumps(
                cbor2.CBORTag(18, cose_sign1),
                canonical=True,
            )

        return cose_sign1_tagged_cbor

    def _calculate_updated_cose_sign1_pad_length(
        self,
        previous_pad_length: int,
        previous_serialized_length: int,
        current_serialized_length: int,
    ) -> int:
        """
        Recalculates the pad length for a COSE_Sign1 (Claim Signature) structure
        so that the total serialized length stays constant despite a variable-length
        TSA token, similar to pad recalculation in the Data Hash Assertion.
        """
        length_difference: int = current_serialized_length - previous_serialized_length

        # If the new token grew by more bytes than the pad has reserved, there is
        # no way to compensate without changing the total signature size, which
        # would break the exclusion boundary for the C2PA structure.
        if length_difference > previous_pad_length:
            raise ValueError("Difference in length exceeds the predefined pad")

        updated_pad_length: int = previous_pad_length - length_difference

        # CBOR encodes a byte-string length header as 1 byte when the length is
        # 0-23, and as 2+ bytes when the length is 24 or more. If the pad drops
        # from >= 24 bytes to < 24 bytes, its own header shrinks by 1 byte.
        # Add 1 byte back to the pad to compensate for that shrinkage and keep
        # the total schema size unchanged.
        if updated_pad_length < 24 <= previous_pad_length:
            updated_pad_length += 1

        # If the pad has been fully consumed and would go negative, there is
        # no valid pad length left to represent — fail loudly instead of
        # silently producing an empty/invalid pad (e.g. b"\x00" * -1 == b"").
        if updated_pad_length < 0:
            raise ValueError("Not enough reserved pad to accommodate the TSA token; increase initial pad size.")

        return updated_pad_length

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
        tsa_sig_structure = ["CounterSignature", serialized_protected_header, b"", cbor2.dumps(signature)]
        serialized_tsa_sig_signature = cbor2.dumps(tsa_sig_structure, canonical=True)

        unprotected_header = self._generate_unprotected_header(serialized_sig_structure=serialized_tsa_sig_signature)

        cose_sign1 = [serialized_protected_header, unprotected_header, None, signature]

        cose_sign1_tagged_cbor = self.serialize_cose_sign1_tagged_with_alignment(cose_sign1)

        return cose_sign1_tagged_cbor
