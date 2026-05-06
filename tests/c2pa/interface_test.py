from pathlib import Path

from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.interface import (
    c2pie_EmplaceManifest,
    c2pie_GenerateActionsAssertion,
    c2pie_GenerateAssertion,
    c2pie_GenerateHashDataAssertion,
    c2pie_GenerateManifest,
    c2pie_GenerateThumbnailAssertion,
)
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import C2PA_ContentTypes

JPEG_HEADER = b"\xff\xd8\xff"
MEDIA_TYPE = "image/jpeg"

KEY_FILEPATH = "tests/credentials/private-key.pem"
CERT_FILEPATH = "tests/credentials/certificate-chain.pub"


def test_generate_assertion_has_correct_type():
    assertion = c2pie_GenerateAssertion(C2PA_AssertionTypes.actions, {})
    assert assertion.type == C2PA_AssertionTypes.actions


def test_generate_assertion_has_correct_schema():
    expected_schema = {
        "actions": [
            {
                "action": "c2pa.created",
            },
        ],
    }
    assertion = c2pie_GenerateAssertion(C2PA_AssertionTypes.actions, expected_schema)
    assert assertion.schema == expected_schema


def test_generate_hash_data_assertion_returns_hash_data_assertion_instance():
    from c2pie.c2pa.assertion import HashDataAssertion

    hash_data_assertion = c2pie_GenerateHashDataAssertion(
        cai_offset=2,
        hashed_data=b"\x00" * 32,
    )
    assert isinstance(hash_data_assertion, HashDataAssertion)


def test_generate_actions_assertion_returns_actions_assertion_instance():
    from c2pie.c2pa.assertion import ActionsAssertion

    actions_assertion = c2pie_GenerateActionsAssertion(action="c2pa.created")
    assert isinstance(actions_assertion, ActionsAssertion)


def test_generate_thumbnail_assertion_returns_thumbnail_assertion_instance():
    from c2pie.c2pa.assertion import ThumbnailAssertion

    thumbnail_assertion = c2pie_GenerateThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert isinstance(thumbnail_assertion, ThumbnailAssertion)


def test_generate_manifest_returns_manifest_store():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
    )

    assert isinstance(manifest_store, ManifestStore)


def test_generate_manifest_contains_one_manifest():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
    )

    assert len(manifest_store.manifests) == 1


def test_generate_manifest_label_follows_urn_c2pa_format():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
    )

    label = manifest_store.manifests[0].get_manifest_label()
    assert label.startswith("urn:c2pa:")


def test_emplace_manifest_returns_bytes_with_jpeg_signature():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()
    with open("tests/test_files/test_image.jpg", "rb") as f:
        jpeg_bytes = f.read()

    assertions = [
        c2pie_GenerateHashDataAssertion(cai_offset=2, hashed_data=b"\x00" * 32),
        c2pie_GenerateActionsAssertion(action="c2pa.created"),
    ]

    manifest_store = c2pie_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
    )

    result = c2pie_EmplaceManifest(
        format_type=C2PA_ContentTypes.jpg,
        content_bytes=jpeg_bytes,
        c2pa_offset=2,
        manifests=manifest_store,
    )

    assert isinstance(result, bytes)
    assert result[:2] == b"\xff\xd8"
