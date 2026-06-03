import uuid

from c2pie.c2pa.assertion import (
    ActionsAssertion,
    Assertion,
    HashDataAssertion,
    IngredientAssertion,
    IngredientThumbnailAssertion,
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
from c2pie.c2pa_parsing.jumbf_parsing import find_in_box
from c2pie.jumbf_boxes.box import Box
from c2pie.jumbf_boxes.description_box import DescriptionBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, get_assertion_label
from c2pie.utils.content_types import C2PA_ContentTypes


def c2pie_GenerateAssertion(assertion_type: C2PA_AssertionTypes, assertion_schema: dict) -> Assertion:
    return Assertion(assertion_type, assertion_schema)


def c2pie_GenerateHashDataAssertion(
    cai_offset: int,
    hashed_data: bytes,
) -> HashDataAssertion:
    return HashDataAssertion(
        cai_offset,
        hashed_data,
    )


def c2pie_GenerateActionsAssertion(
    action: str,
    parameters: dict[str, list[dict[str, str]]] | None = None,
) -> ActionsAssertion:
    return ActionsAssertion(
        action=action,
        parameters=parameters,
    )


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


# Currently not in use.
# If APP11 exceeds the allowed size (65,535 bytes), an error will occur.
# It is necessary to add logic to handle this case by splitting APP11.
def c2pie_GenerateIngredientThumbnailAssertion(
    media_type: str | None = None,
    image_data: bytes | None = None,
    active_manifest: Box | None = None,
) -> SuperBox | IngredientThumbnailAssertion | None:
    if active_manifest:
        possibles_thumbnail_assertion_labels = [
            "c2pa.thumbnail.claim",
            "c2pa.thumbnail.claim.jpeg",
        ]

        previous_thumbnail_assertion = None
        for thumbnail_assertion_label in possibles_thumbnail_assertion_labels:
            previous_thumbnail_assertion = find_in_box(
                active_manifest,
                thumbnail_assertion_label,
            )

            if previous_thumbnail_assertion:
                break

        if previous_thumbnail_assertion:
            ingredient_thumbnail_assertion = SuperBox.from_box(previous_thumbnail_assertion)

            # The type field is used when searching for a Data Hash Assertion
            # in the Assertion Store when the set_hash_data_length() method is called
            ingredient_thumbnail_assertion.type = C2PA_AssertionTypes.ingredient_thumbnail
            
            ingredient_thumbnail_assertion.description_box = DescriptionBox(
                content_type=ingredient_thumbnail_assertion.get_content_type(),
                label=get_assertion_label(C2PA_AssertionTypes.ingredient_thumbnail),
            )
            ingredient_thumbnail_assertion.sync_payload()

            return ingredient_thumbnail_assertion
    else:
        if media_type and image_data:
            return IngredientThumbnailAssertion(
                media_type,
                image_data,
            )

    return None


def c2pie_GenerateIngredientAssertion(
    title: str,
    dc_format: str,
    ingredient_bytes: bytes,
    active_manifest_urn: str | None,
    active_manifest: Box | None,
    ingredient_thumbnail_assertion: IngredientThumbnailAssertion | None = None,
) -> IngredientAssertion:
    return IngredientAssertion(
        title=title,
        dc_format=dc_format,
        ingredient_bytes=ingredient_bytes,
        active_manifest_urn=active_manifest_urn,
        active_manifest=active_manifest,
        ingredient_thumbnail_assertion=ingredient_thumbnail_assertion,
    )


def c2pie_GenerateManifestStore(
    assertions: list,
    private_key: bytes,
    certificate_chain: bytes,
    file_name: str,
    # TODO: #66  : move that variables to configfile
    tsa_url: str | None,
    require_tsa: bool,
    tsa_log_dir: str | None,
    previous_manifest_boxes: list[Manifest] | None = None,
) -> ManifestStore:
    """
    private_key: PKCS#8 PEM (RSA) bytes
    certificate_chain: PEM bundle (leaf + intermediates, NO root) bytes
    previous_manifest_boxes: raw JUMBF bytes of manifests from a previous signing (preserved in the store)
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

    return ManifestStore([*(previous_manifest_boxes or []), manifest])


def c2pie_EmplaceManifest(
    format_type: C2PA_ContentTypes,
    content_bytes: bytes,
    c2pa_offset: int,
    manifest_store: ManifestStore,
) -> bytes:
    if format_type == C2PA_ContentTypes.jpg or format_type == C2PA_ContentTypes.jpeg:
        assumed_hash_data_len = 0
        final_length = -1
        tail = b""

        for _ in range(RETRY_SIGNATURE):
            manifest_store.set_hash_data_length_for_all(assumed_hash_data_len)

            payload = manifest_store.serialize()
            storage = JpgSegmentApp11Storage(
                app11_segment_box_length=manifest_store.get_length(),
                app11_segment_box_type=manifest_store.get_type(),
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
        return emplace_manifest_into_pdf(content_bytes, manifest_store)

    raise ValueError(f"Unsupported content type {format_type}!")
