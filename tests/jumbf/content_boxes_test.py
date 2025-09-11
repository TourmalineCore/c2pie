from c2pie.jumbf_boxes.content_box import ContentBox


def test_create_content_box():
    test_content_box = ContentBox()

    assert test_content_box.t_box == b"json".hex()


def test_create_content_box_with_payload():
    test_content_box = ContentBox(payload=b"0000")

    assert test_content_box.payload == b"0000"


def test_serialize_content_box():
    test_content_box = ContentBox(payload=b"\x00\x00")

    test_content_box_serialized_data = b"\x00\x00\x00\x0a" + b"\x6a\x73\x6f\x6e" + b"\x00\x00"

    assert test_content_box.serialize() == test_content_box_serialized_data
