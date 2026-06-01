from c2pie.c2pa.assertion import IngredientThumbnailAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import jumbf_content_types

TEST_DATA = b"\x00\x00\x00"
MEDIA_TYPE = "image/jpeg"


def test_ingredient_thumbnail_assertion_is_jumb_super_box():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert ingredient_thumbnail_assertion.t_box == b"jumb".hex()


def test_ingredient_thumbnail_assertion_has_correct_assertion_type():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert ingredient_thumbnail_assertion.type == C2PA_AssertionTypes.ingredient_thumbnail


def test_ingredient_thumbnail_assertion_has_correct_content_type():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert ingredient_thumbnail_assertion.get_content_type() == jumbf_content_types["embedded_file"]


def test_ingredient_thumbnail_assertion_has_correct_label():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert ingredient_thumbnail_assertion.get_label() == "c2pa.thumbnail.ingredient"


def test_thumbnail_assertion_contains_two_correct_boxes():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert len(ingredient_thumbnail_assertion.content_boxes) == 2
    assert ingredient_thumbnail_assertion.content_boxes[0].get_type() == b"bfdb".hex()
    assert ingredient_thumbnail_assertion.content_boxes[1].get_type() == b"bidb".hex()


def test_ingredient_thumbnail_assertion_has_correct_bfdb_payload_lenght():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )
    bfdb_payload = ingredient_thumbnail_assertion.content_boxes[0].get_payload()

    assert len(bfdb_payload) == MEDIA_TYPE.encode("utf-8") + 2


def test_ingredient_thumbnail_assertion_has_correct_toggles_inside_bfdb_payload():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )
    bfdb_payload = ingredient_thumbnail_assertion.content_boxes[0].get_payload()

    assert bfdb_payload[0:1] == b"\x00"


def test_ingredient_thumbnail_assertion_has_correct_media_type_inside_bfdb_payload():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )
    bfdb_payload = ingredient_thumbnail_assertion.content_boxes[0].get_payload()

    assert MEDIA_TYPE.encode("utf-8") in bfdb_payload


def test_ingredient_thumbnail_assertion_bfdb_payload_media_type_is_null_terminated():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )
    bfdb_payload = ingredient_thumbnail_assertion.content_boxes[0].get_payload()

    assert bfdb_payload[-1:] == b"\x00"


def test_ingredient_thumbnail_assertion_bidb_payload_contains_correct_data():
    ingredient_thumbnail_assertion = IngredientThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=TEST_DATA,
    )

    assert ingredient_thumbnail_assertion.content_boxes[1].get_payload() == TEST_DATA
