from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.c2pa.assertions.ingredient_thumbnail_assertion import IngredientThumbnailAssertion
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.interface import (
    c2pie_EmplaceManifest,
    c2pie_GenerateActionsAssertion,
    c2pie_GenerateAssertion,
    c2pie_GenerateHashDataAssertion,
    c2pie_GenerateIngredientThumbnailAssertion,
    c2pie_GenerateManifestStore,
    c2pie_GenerateThumbnailAssertion,
)
from c2pie.jumbf_boxes.super_box import SuperBox
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

    expected_assertion_content_boxes = Assertion.content_box_from_schema(C2PA_AssertionTypes.actions, expected_schema)

    assert len(assertion.content_boxes) == len(expected_assertion_content_boxes)
    for actual, expected in zip(assertion.content_boxes, expected_assertion_content_boxes, strict=False):
        assert actual.get_type() == expected.get_type()
        assert actual.payload == expected.payload


def test_generate_hash_data_assertion_returns_hash_data_assertion_instance():
    from c2pie.c2pa.assertions.hash_data_assertion import HashDataAssertion

    hash_data_assertion = c2pie_GenerateHashDataAssertion(
        hashed_data=b"\x00" * 32,
    )
    assert isinstance(hash_data_assertion, HashDataAssertion)


def test_generate_actions_assertion_returns_actions_assertion_instance():
    from c2pie.c2pa.assertions.actions_assertion import ActionsAssertion

    actions_assertion = c2pie_GenerateActionsAssertion(action="c2pa.created")
    assert isinstance(actions_assertion, ActionsAssertion)


def test_generate_thumbnail_assertion_returns_thumbnail_assertion_instance():
    from c2pie.c2pa.assertions.thumbnail_assertion import ThumbnailAssertion

    thumbnail_assertion = c2pie_GenerateThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert isinstance(thumbnail_assertion, ThumbnailAssertion)


def test_generate_ingredient_thumbnail_assertion_returns_ingredient_thumbnail_assertion_instance():
    ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )

    assert isinstance(ingredient_thumbnail_assertion, IngredientThumbnailAssertion)


def test_generate_ingredient_thumbnail_assertion_returns_none_when_no_arguments():
    ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion()

    assert ingredient_thumbnail_assertion is None


def test_generate_ingredient_thumbnail_assertion_returns_none_when_only_media_type_given():
    ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion(media_type=MEDIA_TYPE)

    assert ingredient_thumbnail_assertion is None


def test_generate_ingredient_thumbnail_assertion_returns_none_when_only_image_data_given():
    ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion(image_data=JPEG_HEADER)

    assert ingredient_thumbnail_assertion is None


def test_generate_ingredient_thumbnail_assertion_with_active_manifest_and_no_thumbnail_returns_none():
    mock_manifest = MagicMock()

    with patch("c2pie.interface.find_in_box", return_value=None):
        ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion(active_manifest=mock_manifest)

    assert ingredient_thumbnail_assertion is None


def test_generate_ingredient_thumbnail_assertion_with_active_manifest_and_found_thumbnail_returns_super_box():
    mock_manifest = MagicMock()
    mock_super_box = MagicMock(spec=SuperBox)

    with patch("c2pie.interface.find_in_box", return_value=MagicMock()):
        with patch("c2pie.interface.SuperBox.from_box", return_value=mock_super_box):
            ingredient_thumbnail_assertion = c2pie_GenerateIngredientThumbnailAssertion(active_manifest=mock_manifest)

    assert ingredient_thumbnail_assertion is mock_super_box


def test_generate_ingredient_thumbnail_assertion_with_active_manifest_sets_ingredient_thumbnail_type():
    mock_manifest = MagicMock()
    mock_super_box = MagicMock(spec=SuperBox)

    with patch("c2pie.interface.find_in_box", return_value=MagicMock()):
        with patch("c2pie.interface.SuperBox.from_box", return_value=mock_super_box):
            c2pie_GenerateIngredientThumbnailAssertion(active_manifest=mock_manifest)

    assert mock_super_box.type == C2PA_AssertionTypes.ingredient_thumbnail


def test_generate_ingredient_thumbnail_assertion_with_active_manifest_sets_correct_description_label():
    mock_manifest = MagicMock()
    mock_super_box = MagicMock(spec=SuperBox)

    with patch("c2pie.interface.find_in_box", return_value=MagicMock()):
        with patch("c2pie.interface.SuperBox.from_box", return_value=mock_super_box):
            c2pie_GenerateIngredientThumbnailAssertion(active_manifest=mock_manifest)

    assert mock_super_box.description_box.label == "c2pa.thumbnail.ingredient"


def test_generate_manifest_returns_manifest_store():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )

    assert isinstance(manifest_store, ManifestStore)


def test_generate_manifest_contains_one_manifest():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )

    assert len(manifest_store.manifests) == 1


def test_generate_manifest_label_follows_urn_c2pa_format():
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    assertions = [c2pie_GenerateActionsAssertion(action="c2pa.created")]
    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
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
        c2pie_GenerateHashDataAssertion(hashed_data=b"\x00" * 32),
        c2pie_GenerateActionsAssertion(action="c2pa.created"),
    ]

    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=Path("test.jpg").name,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )

    result = c2pie_EmplaceManifest(
        format_type=C2PA_ContentTypes.jpg,
        content_bytes=jpeg_bytes,
        c2pa_offset=2,
        manifest_store=manifest_store,
    )

    assert isinstance(result, bytes)
    assert result[:2] == b"\xff\xd8"


FIXTURES_FOLDER_PATH = Path(__file__).parent.parent / "test_files"

test_cases = [
    Path(FIXTURES_FOLDER_PATH / "test_image.jpg"),
    Path(FIXTURES_FOLDER_PATH / "test_doc.pdf"),
]


@pytest.mark.parametrize(
    "file",
    test_cases,
    ids=lambda x: x.suffix[1:],
)
def test_calculated_exclusion_covers_the_full_storage(file):
    with open(KEY_FILEPATH, "rb") as f:
        key = f.read()
    with open(CERT_FILEPATH, "rb") as f:
        cert = f.read()

    with open(file, "rb") as f:
        raw_bytes = f.read()

    assertions = [
        c2pie_GenerateHashDataAssertion(
            hashed_data=b"\x00" * 32,
        ),
    ]

    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=cert,
        file_name=file.name,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )

    file_extension = C2PA_ContentTypes(file.suffix)

    if file_extension == C2PA_ContentTypes.jpeg or file_extension == C2PA_ContentTypes.jpg:
        """
        Expected length of serialized data in JPEG/JPG format consists 
        of APP11 segment header + payload (serialized ManifestStore).

        More info about APP11 segment you can see here: docs/JPG-structure-overview.md
        """
        expected_serialized_length = 2 + 2 + 2 + 2 + 4 + len(manifest_store.serialize())
    elif file_extension == C2PA_ContentTypes.pdf:
        """
        Expected length of serialized data in PDF format consists 
        of body (serialized ManifestStore) + updated cross-ref table and trailer.

        More info about PDF Incremental Update you can see here: docs/PDF-structure-overview.md
        """
        expected_serialized_length = 7165

    with patch("c2pie.c2pa.manifest_store.ManifestStore.add_full_c2pa_structure_exclusion") as mock_func:
        c2pie_EmplaceManifest(
            format_type=file_extension,
            content_bytes=raw_bytes,
            c2pa_offset=2,
            manifest_store=manifest_store,
        )

        last_call = mock_func.call_args

        assert expected_serialized_length == last_call.args[1]
