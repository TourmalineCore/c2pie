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
from c2pie.utils.content_types import c2pa_content_types


def _split_pem_certs_to_der(pem_bytes: bytes) -> list[bytes]:
    if not pem_bytes:
        return []
    blocks = re.findall(
        b"-----BEGIN CERTIFICATE-----\\s.*?-----END CERTIFICATE-----\\s*",
        pem_bytes,
        flags=re.DOTALL,
    )
    ders: list[bytes] = []
    for blk in blocks:
        cert = x509.load_pem_x509_certificate(blk)
        ders.append(cert.public_bytes(Encoding.DER))
    return ders


class ClaimSignature(SuperBox):
    """
    COSE_Sign1 (PS256), detached:
      - protected: {1:-37, 33:[x5chain DER...]}
      - unprotected: {}
      - COSE payload = nil
      - Sig_structure payload = bstr(Claim CBOR)
    """

    def __init__(
        self,
        claim: Claim,
        *,
        private_key: bytes,
        certificate_pem_bundle: bytes,
        certificate: bytes = None,
    ):
        if certificate_pem_bundle is None and certificate is not None:
            certificate_pem_bundle = certificate

        self.claim = claim
        self.private_key = private_key
        self.certificate = certificate_pem_bundle

        content_boxes = self._generate_payload()
        super().__init__(
            content_type=c2pa_content_types["claim_signature"],
            label="c2pa.signature",
            content_boxes=content_boxes,
        )

    def _generate_payload(self) -> list[ContentBox]:
        if not (self.claim and self.private_key and self.certificate):
            return []

        cose_tagged = self._create_cose_sign1()
        return [ContentBox(box_type=b"cbor".hex(), payload=cose_tagged)]

    def set_claim(self, claim: Claim):
        self.claim = claim
        content_boxes = self._generate_payload()
        super().__init__(
            content_type=c2pa_content_types["claim_signature"],
            label="c2pa.signature",
            content_boxes=content_boxes,
        )

    def _generate_protected_header(self) -> bytes:
        der_chain = _split_pem_certs_to_der(self.certificate or b"")
        protected: dict[int, Any] = {1: -37}
        if der_chain:
            protected[33] = der_chain
        return cbor2.dumps(protected, canonical=True)

    def _create_cose_sign1(self) -> bytes:
        phdr_serialized = self._generate_protected_header()
        claim_cbor = self.claim.get_cbor_payload()
        sig_structure = ["Signature1", phdr_serialized, b"", claim_cbor]
        to_sign = cbor2.dumps(sig_structure, canonical=True)

        key = serialization.load_pem_private_key(self.private_key, password=None)
        signature = key.sign(  # type: ignore
            to_sign,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),  # type: ignore
            hashes.SHA256(),  # type: ignore
        )

        cose_msg = [phdr_serialized, {}, None, signature]
        return cbor2.dumps(cbor2.CBORTag(18, cose_msg), canonical=True)
