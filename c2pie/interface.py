from __future__ import annotations

import uuid

from c2pie.c2pa.assertion import (
    ActionsAssertion,
    Assertion,
    HashDataAssertion,
    ThumbnailAssertion,
)
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.c2pa.claim_signature import ClaimSignature
from c2pie.c2pa.config import RETRY_SIGNATURE
from c2pie.c2pa.manifest import Manifest
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.c2pa_injection.jpg_injection import JpgSegmentApp11Storage
from c2pie.c2pa_injection.pdf_injection import emplace_manifest_into_pdf
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import C2PA_ContentTypes


def c2pie_GenerateAssertion(assertion_type: C2PA_AssertionTypes, assertion_schema: dict) -> Assertion:
    return Assertion(assertion_type, assertion_schema)


def c2pie_GenerateHashDataAssertion(cai_offset: int, hashed_data: bytes) -> HashDataAssertion:
    return HashDataAssertion(cai_offset, hashed_data)


def c2pie_GenerateActionsAssertion(
    action: str,
    parameters: dict[str, list[dict[str, str]]] | None = None,
) -> ActionsAssertion:
    return ActionsAssertion(action, parameters)


# Currently not in use.
# If APP11 exceeds the allowed size (65,535 bytes), an error will occur.
# It is necessary to add logic to handle this case by splitting APP11.
def c2pie_GenerateThumbnailAssertion(
    media_type: str,
    image_data: bytes,
) -> ThumbnailAssertion:
    return ThumbnailAssertion(
        media_type=media_type,
        image_data=image_data,
    )


def c2pie_GenerateManifest(
    assertions: list,
    private_key: bytes,
    certificate_chain: bytes,
    file_name: str,
    # TODO: #66  : move that variables to configfile
    tsa_url: str | None,
    require_tsa: bool,
    tsa_log_dir: str | None,
) -> ManifestStore:
    """
    private_key: PKCS#8 PEM (RSA) bytes
    certificate_chain: PEM bundle (leaf + intermediates, NO root) bytes
    """

    manifest_label = f"urn:c2pa:{uuid.uuid4().hex}"
    manifest = Manifest(manifest_label=manifest_label)

    assertion_store = AssertionStore(assertions=assertions)
    manifest.set_assertion_store(assertion_store)

    claim = Claim(
        manifest_label=manifest.get_manifest_label(),
        assertion_store=assertion_store,
        dc_title=file_name,
    )
    manifest.set_claim(claim)

    claim_signature = ClaimSignature(
        claim=claim,
        private_key=private_key,
        certificate_pem_bundle=certificate_chain,
        tsa_url=tsa_url,
        require_tsa=require_tsa,
        tsa_log_dir=tsa_log_dir,
    )
    manifest.set_claim_signature(claim_signature)

    return ManifestStore([manifest])


def c2pie_EmplaceManifest(
    format_type: C2PA_ContentTypes,
    content_bytes: bytes,
    c2pa_offset: int,
    manifests: ManifestStore,
) -> bytes:
    if hasattr(manifests, "manifests"):
        for manifest in manifests.manifests:
            claim = getattr(manifest, "claim", None)
            if claim is not None and hasattr(claim, "set_format"):
                if format_type == C2PA_ContentTypes.jpg or format_type == C2PA_ContentTypes.jpeg:
                    claim.set_format("image/jpg")
                elif format_type == C2PA_ContentTypes.pdf:
                    claim.set_format("application/pdf")

    if format_type == C2PA_ContentTypes.jpg or format_type == C2PA_ContentTypes.jpeg:
        assumed_hash_data_len = 0
        final_length = -1
        tail = b""
        for _ in range(RETRY_SIGNATURE):
            manifests.set_hash_data_length_for_all(assumed_hash_data_len)
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
            assumed_hash_data_len = total_len
        return content_bytes[:c2pa_offset] + tail + content_bytes[c2pa_offset:]

    if format_type == C2PA_ContentTypes.pdf:
        return emplace_manifest_into_pdf(content_bytes, manifests)

    raise ValueError(f"Unsupported content type {format_type}!")
