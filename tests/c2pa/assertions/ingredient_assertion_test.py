import hashlib
from unittest.mock import MagicMock, patch

from c2pie.c2pa.assertion import IngredientAssertion
from c2pie.c2pa.claim_signature import ClaimSignature
from c2pie.c2pa.manifest import Manifest
from c2pie.c2pa_parsing.jumbf_parsing import find_in_box
from c2pie.jumbf_boxes.box import Box
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from tests.helpers.jumbf_generators import _mock_make_superbox

TITLE = "test-ingredient.pdf"
DC_FORMAT = "application/pdf"
INGREDIENT_BYTES = b"fake-pdf-content"
ACTIVE_URN = "urn:c2pa:test-manifest"
VALIDATION_RESULTS = {"status": []}


def test_ingredient_assertion_schema_is_correct():
    ingredient_assertion = IngredientAssertion(
        TITLE,
        DC_FORMAT,
        INGREDIENT_BYTES,
        None,
        [],
    )
    assert ingredient_assertion.type == C2PA_AssertionTypes.ingredient
    assert ingredient_assertion.get_label() == "c2pa.ingredient.v3"
    assert ingredient_assertion.schema["dc:title"] == TITLE
    assert ingredient_assertion.schema["dc:format"] == DC_FORMAT
    assert ingredient_assertion.schema["relationship"] == "parentOf"
    assert "activeManifest" not in ingredient_assertion.schema
    assert "validationResults" not in ingredient_assertion.schema


def test_no_active_manifest_when_boxes_empty():
    ingredient_assertion = IngredientAssertion(
        TITLE,
        DC_FORMAT,
        INGREDIENT_BYTES,
        ACTIVE_URN,
        [],
    )
    assert "activeManifest" not in ingredient_assertion.schema


def test_no_active_manifest_when_validation_fails():
    with patch(
        "c2pie.c2pa.assertion.IngredientAssertion.validate_ingredient",
        return_value=None,
    ):
        manifest_box, _ = Box.parse_from_bytes(
            _mock_make_superbox(ACTIVE_URN),
        )
        ingredient_assertion = IngredientAssertion(
            TITLE,
            DC_FORMAT,
            INGREDIENT_BYTES,
            ACTIVE_URN,
            [manifest_box],
        )

    assert "activeManifest" not in ingredient_assertion.schema
    assert "validationResults" not in ingredient_assertion.schema


def test_no_active_manifest_when_box_not_found():
    with patch(
        "c2pie.c2pa.assertion.IngredientAssertion.validate_ingredient",
        return_value=VALIDATION_RESULTS,
    ):
        manifest_box, _ = Box.parse_from_bytes(
            _mock_make_superbox("urn:c2pa:other-manifest"),
        )
        ingredient_assertion = IngredientAssertion(
            TITLE,
            DC_FORMAT,
            INGREDIENT_BYTES,
            None,
            None,
        )

    assert "activeManifest" not in ingredient_assertion.schema


def test_ingredient_assertion_schema_with_active_manifest_is_correct():
    with patch(
        "c2pie.c2pa.assertion.IngredientAssertion.validate_ingredient",
        return_value=VALIDATION_RESULTS,
    ):
        manifest = Manifest(manifest_label="urn:c2pa:test-manifest")

        with patch.object(ClaimSignature, "_generate_payload", return_value=[]):
            claim = MagicMock()
            claim_signature = ClaimSignature(
                claim=claim,
                private_key=b"\x00\x00\x00",
                tsa_url=None,
                require_tsa=False,
                tsa_log_dir=None,
            )
            manifest.set_claim_signature(claim_signature)

        ingredient_assertion = IngredientAssertion(
            TITLE,
            DC_FORMAT,
            INGREDIENT_BYTES,
            ACTIVE_URN,
            manifest,
        )

    active_manifest_expected_hash = hashlib.sha256(manifest.get_payload()).digest()

    claim_signature_box = find_in_box(manifest, "c2pa.signature")
    claim_signature_expected_hash = hashlib.sha256(claim_signature_box.get_payload()).digest()

    assert ingredient_assertion.schema["activeManifest"]["url"] == f"self#jumbf=/c2pa/{ACTIVE_URN}"
    assert ingredient_assertion.schema["activeManifest"]["hash"] == active_manifest_expected_hash
    assert ingredient_assertion.schema["activeManifest"]["alg"] == "sha256"

    assert ingredient_assertion.schema["validationResults"] == VALIDATION_RESULTS

    assert ingredient_assertion.schema["claimSignature"]["url"] == f"self#jumbf=/c2pa/{ACTIVE_URN}/c2pa.signature"
    assert ingredient_assertion.schema["claimSignature"]["hash"] == claim_signature_expected_hash
    assert ingredient_assertion.schema["claimSignature"]["alg"] == "sha256"
