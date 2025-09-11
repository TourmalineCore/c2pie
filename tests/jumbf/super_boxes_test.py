from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import jumbf_content_types


def test_create_super_box():
    test_super_box = SuperBox()

    assert test_super_box.t_box == b"jumb".hex()


def test_create_super_box_with_description_box():
    test_super_box = SuperBox()

    assert test_super_box.description_box is not None


def test_create_super_box_with_cbor_content_type():
    test_super_box = SuperBox(content_type=jumbf_content_types["cbor"])

    assert test_super_box.description_box.content_type == jumbf_content_types["cbor"]


def test_create_super_box_with_label():
    test_super_box = SuperBox(label="c2pa.Test")

    assert test_super_box.description_box.label == "c2pa.Test"


def test_create_super_box_without_content_boxes():
    test_super_box = SuperBox()

    assert len(test_super_box.content_boxes) == 0


def test_serialize_super_box():
    test_super_box = SuperBox(label="super")

    test_serialized_data = (
        b"\x00\x00\x00\x27"
        + b"\x6a\x75\x6d\x62"
        + b"\x00\x00\x00\x1f"
        + b"\x6a\x75\x6d\x64"
        + b"\x6a\x73\x6f\x6e\x00\x11\x00\x10\x80\x00\x00\xaa\x00\x38\x9b\x71"
        + b"\x03"
        + b"\x73\x75\x70\x65\x72"
        + b"\x00"
    )

    print(test_super_box.get_length())

    assert test_super_box.serialize() == test_serialized_data


def test_serialize_super_box_with_content_box():
    test_super_box = SuperBox(label="super")

    test_content_box = ContentBox(payload=b"\x00\x00")
    test_super_box.add_content_box(test_content_box)
    test_super_box.sync_payload()

    test_serialized_data = (
        b"\x00\x00\x00\x31"
        + b"\x6a\x75\x6d\x62"
        + b"\x00\x00\x00\x1f"
        + b"\x6a\x75\x6d\x64"
        + b"\x6a\x73\x6f\x6e\x00\x11\x00\x10\x80\x00\x00\xaa\x00\x38\x9b\x71"
        + b"\x03"
        + b"\x73\x75\x70\x65\x72"
        + b"\x00"
        + b"\x00\x00\x00\x0a"
        + b"\x6a\x73\x6f\x6e"
        + b"\x00\x00"
    )

    assert test_super_box.serialize() == test_serialized_data
