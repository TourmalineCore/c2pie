from c2pie.c2pa.assertions.embedded_data_assertion import EmbeddedDataAssertion
from c2pie.utils.content_types import jumbf_content_types

JPEG_HEADER = b"\xff\xd8\xff"
MEDIA_TYPE = "image/jpeg"


def test_embedded_data_assertion_is_jumb_super_box():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.t_box == b"jumb".hex()


def test_embedded_data_assertion_content_type_is_embedded_file():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.get_content_type() == jumbf_content_types["embedded_file"]


def test_embedded_data_assertion_label():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.get_label() == "c2pa.embedded-data"


def test_embedded_data_assertion_has_two_content_boxes():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert len(embedded_data_assertion.content_boxes) == 2


def test_embedded_data_assertion_first_box_is_bfdb():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.content_boxes[0].get_type() == b"bfdb".hex()


def test_embedded_data_assertion_second_box_is_bidb():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.content_boxes[1].get_type() == b"bidb".hex()


def test_embedded_data_assertion_bfdb_payload_first_byte_is_toggles():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = embedded_data_assertion.content_boxes[0].get_payload()
    assert bfdb_payload[0:1] == b"\x00"


def test_embedded_data_assertion_bfdb_payload_contains_media_type():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = embedded_data_assertion.content_boxes[0].get_payload()
    assert MEDIA_TYPE.encode("utf-8") in bfdb_payload


def test_embedded_data_assertion_bfdb_payload_media_type_is_null_terminated():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = embedded_data_assertion.content_boxes[0].get_payload()
    assert bfdb_payload[-1:] == b"\x00"


def test_embedded_data_assertion_bfdb_payload_structure():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    bfdb_payload = embedded_data_assertion.content_boxes[0].get_payload()
    expected = b"\x00" + MEDIA_TYPE.encode("utf-8") + b"\x00"
    assert bfdb_payload == expected


def test_embedded_data_assertion_bfdb_uses_passed_media_type():
    custom_type = "image/png"
    embedded_data_assertion = EmbeddedDataAssertion(media_type=custom_type, image_data=b"\x89PNG")
    bfdb_payload = embedded_data_assertion.content_boxes[0].get_payload()
    expected = b"\x00" + custom_type.encode("utf-8") + b"\x00"
    assert bfdb_payload == expected


def test_embedded_data_assertion_bidb_contains_image_data():
    embedded_data_assertion = EmbeddedDataAssertion(
        media_type=MEDIA_TYPE,
        image_data=JPEG_HEADER,
    )
    assert embedded_data_assertion.content_boxes[1].get_payload() == JPEG_HEADER
