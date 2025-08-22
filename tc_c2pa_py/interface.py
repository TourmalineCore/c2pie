from __future__ import annotations

from tc_c2pa_py.c2pa.assertion import Assertion, HashDataAssertion
from tc_c2pa_py.c2pa.assertion_store import AssertionStore
from tc_c2pa_py.c2pa.claim import Claim
from tc_c2pa_py.c2pa.claim_signature import ClaimSignature
from tc_c2pa_py.c2pa.config import RETRY_SIGNATURE
from tc_c2pa_py.c2pa.manifest import Manifest
from tc_c2pa_py.c2pa.manifest_store import ManifestStore
from tc_c2pa_py.c2pa_injection.jpeg_injection import JpgSegmentApp11Storage
from tc_c2pa_py.c2pa_injection.pdf_injection import emplace_manifest_into_pdf
from tc_c2pa_py.utils.assertion_schemas import C2PA_AssertionTypes
from tc_c2pa_py.utils.content_types import C2PA_ContentTypes


def TC_C2PA_GenerateAssertion(assertion_type: C2PA_AssertionTypes, assertion_schema) -> Assertion:
    return Assertion(assertion_type, assertion_schema)


def TC_C2PA_GenerateHashDataAssertion(cai_offset: int, hashed_data: bytes) -> HashDataAssertion:
    return HashDataAssertion(cai_offset, hashed_data)


def TC_C2PA_GenerateManifest(assertions, private_key: bytes, certificate_chain: bytes) -> ManifestStore:
    """
    private_key: PKCS#8 PEM (RSA) bytes
    certificate_chain: PEM bundle (leaf + intermediates, NO root) bytes
    """
    manifest = Manifest()

    assertion_store = AssertionStore(assertions=assertions)
    manifest.set_assertion_store(assertion_store)

    claim = Claim(
        claim_generator="tc_c2pa_py",
        manifest_label=manifest.get_manifest_label(),
        assertion_store=assertion_store,
    )
    manifest.set_claim(claim)

    claim_signature = ClaimSignature(
        claim,
        private_key=private_key,
        certificate_pem_bundle=certificate_chain,
    )
    manifest.set_claim_signature(claim_signature)

    return ManifestStore([manifest])


def TC_C2PA_EmplaceManifest(
    format_type: C2PA_ContentTypes,
    content_bytes: bytes,
    c2pa_offset: int,
    manifests: ManifestStore,
) -> bytes:
    if hasattr(manifests, "manifests"):
        for manifest in manifests.manifests:
            claim = getattr(manifest, "claim", None)
            if claim is not None and hasattr(claim, "set_format"):
                if format_type == C2PA_ContentTypes.jpg:
                    claim.set_format("image/jpeg")
                elif format_type == C2PA_ContentTypes.pdf:
                    claim.set_format("application/pdf")

    if format_type == C2PA_ContentTypes.jpg:
        guessed_length = 0
        final_length = -1
        tail = b""
        for _ in range(RETRY_SIGNATURE):
            manifests.set_hash_data_length_for_all(guessed_length)
            payload = manifests.serialize()
            storage = JpgSegmentApp11Storage(
                app11_segment_box_length=manifests.get_length(),
                app11_segment_box_type=manifests.get_type(),
                payload=payload,
            )
            tail = storage.serialize()
            total_len = len(tail)
            if total_len == final_length:
                break
            final_length = total_len
            guessed_length = total_len
        return content_bytes[:c2pa_offset] + tail + content_bytes[c2pa_offset:]

    if format_type == C2PA_ContentTypes.pdf:
        return emplace_manifest_into_pdf(content_bytes, manifests)

    print(f"Unsupported content type {format_type}!")
    return b""
