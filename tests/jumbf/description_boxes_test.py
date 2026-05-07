from c2pie.jumbf_boxes.box import Box
from c2pie.jumbf_boxes.description_box import DescriptionBox
from c2pie.utils.content_types import jumbf_content_types


def test_create_description_box():
    test_description_box = DescriptionBox()

    assert test_description_box.t_box == b"jumd".hex()


def test_create_description_box_with_label():
    test_description_box = DescriptionBox(label="test")

    assert test_description_box.label == "test"


def test_create_description_box_with_content_type():
    test_description_box = DescriptionBox(content_type=jumbf_content_types["json"])

    assert test_description_box.content_type == jumbf_content_types["json"]


def test_create_description_box_with_toggle():
    test_description_box = DescriptionBox()

    assert test_description_box.toggle == 3


def test_description_box_check_length():
    test_description_box = DescriptionBox()

    assert test_description_box.get_length() == 26


def test_description_box_serialize():
    test_description_box = DescriptionBox(label="a")

    test_serialized_data = (
        b"\x00\x00\x00\x1b"
        + b"\x6a\x75\x6d\x64"
        + b"\x6a\x73\x6f\x6e\x00\x11\x00\x10\x80\x00\x00\xaa\x00\x38\x9b\x71"
        + b"\x03"
        + b"\x61"
        + b"\x00"
    )

    assert test_description_box.serialize() == test_serialized_data


def test_description_box_from_box():
    original = DescriptionBox(
        content_type=jumbf_content_types["json"],
        label="test-label",
    )
    raw = original.serialize()

    parsed_box, _ = Box.parse_from_bytes(raw)
    restored = DescriptionBox.from_box(parsed_box)

    assert restored.get_label() == "test-label"
    assert restored.get_content_type() == jumbf_content_types["json"]
    assert restored.get_length() == original.get_length()


def test_description_box_from_box_empty_label():
    original = DescriptionBox(
        content_type=jumbf_content_types["json"],
        label="",
    )
    raw = original.serialize()

    parsed_box, _ = Box.parse_from_bytes(raw)
    restored = DescriptionBox.from_box(parsed_box)

    assert restored.get_label() == ""


def test_description_box_from_box_short_payload():
    bad_box = Box(
        b"jumd".hex(),
        payload=b"\x00" * 17,
    )

    try:
        DescriptionBox.from_box(bad_box)
        raise AssertionError("Should have raised")
    except ValueError as e:
        assert "too short" in str(e) or "null-terminated" in str(e)


def test_description_box_from_box_no_terminator():
    payload = jumbf_content_types["json"] + b"\x03" + b"no-null-byte"
    bad_box = Box(b"jumd".hex(), payload=payload)

    try:
        DescriptionBox.from_box(bad_box)
        raise AssertionError("Should have raised")
    except ValueError as e:
        assert "null-terminated" in str(e)
