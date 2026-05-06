from c2pie.c2pa.assertion import ThumbnailAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import jumbf_content_types

JPEG_HEADER = b"\xff\xd8\xff"
MEDIA_TYPE = "image/jpeg"


def test_thumbnail_assertion_is_jumb_super_box():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.t_box == b"jumb".hex()


def test_thumbnail_assertion_type_is_thumbnail():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.type == C2PA_AssertionTypes.thumbnail


def test_thumbnail_assertion_content_type_is_embedded_file():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.get_content_type() == jumbf_content_types["embedded_file"]


def test_thumbnail_assertion_label():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.get_label() == "c2pa.thumbnail.claim"


def test_thumbnail_assertion_has_two_content_boxes():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert len(thumbnail_assertion.content_boxes) == 2


def test_thumbnail_assertion_contains_valid_boxes():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.content_boxes[0].get_type() == b"bfdb".hex()
    assert thumbnail_assertion.content_boxes[1].get_type() == b"bidb".hex()


def test_thumbnail_assertion_bfdb_payload_first_byte_is_toggles():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = thumbnail_assertion.content_boxes[0].get_payload()
    assert bfdb_payload[0:1] == b"\x00"


def test_thumbnail_assertion_bfdb_payload_contains_media_type():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = thumbnail_assertion.content_boxes[0].get_payload()
    assert MEDIA_TYPE.encode("utf-8") in bfdb_payload


def test_thumbnail_assertion_bfdb_payload_media_type_is_null_terminated():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = thumbnail_assertion.content_boxes[0].get_payload()
    assert bfdb_payload[-1:] == b"\x00"


def test_thumbnail_assertion_bfdb_payload_structure():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = thumbnail_assertion.content_boxes[0].get_payload()
    expected_bfdb_payload = b"\x00" + MEDIA_TYPE.encode("utf-8") + b"\x00"
    assert bfdb_payload == expected_bfdb_payload


def test_thumbnail_assertion_bidb_contains_image_data():
    thumbnail_assertion = ThumbnailAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert thumbnail_assertion.content_boxes[1].get_payload() == JPEG_HEADER


def test_thumbnail_assertion_bfdb_uses_passed_media_type():
    custom_type = "application/pdf"
    thumbnail_assertion = ThumbnailAssertion(
        media_type=custom_type,
        image_data=b"\x89PDF",
    )
    bfdb_payload = thumbnail_assertion.content_boxes[0].get_payload()
    expected_bfdb_payload = b"\x00" + custom_type.encode("utf-8") + b"\x00"
    assert bfdb_payload == expected_bfdb_payload


def test_thumbnail_assertion_bidb_uses_passed_image_data():
    custom_type = "application/pdf"
    custom_data = b"\x89PDF\r\n\x1a\n"
    thumbnail_assertion = ThumbnailAssertion(
        media_type=custom_type,
        image_data=custom_data,
    )
    assert thumbnail_assertion.content_boxes[1].get_payload() == custom_data
