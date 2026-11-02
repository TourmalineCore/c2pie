from c2pie.jumbf_boxes.box import Box, iter_boxes


def test_create_box():
    test_box = Box(b"jumb".hex())

    assert test_box.t_box == b"jumb".hex()


def test_get_some_box_length():
    test_box = Box(b"jumb".hex())

    assert test_box.get_length() is not None


def test_get_true_box_length():
    test_box = Box(b"jumb".hex())

    assert test_box.get_length() == 8


def test_get_box_type():
    test_box = Box(b"jumb".hex())

    assert test_box.get_type() == b"jumb".hex()


def test_serialize_box():
    expected_serialized_data = b"\x00\x00\x00\x08\x6a\x75\x6d\x62"

    test_box = Box(b"jumb".hex())

    assert test_box.serialize() == expected_serialized_data


def test_parse_from():
    expected_serialized_data = b"\x00\x00\x00\x08\x6a\x75\x6d\x62"

    parsed_box, end_offset = Box.parse_from_bytes(expected_serialized_data)

    assert parsed_box.get_type() == b"jumb".hex()
    assert parsed_box.get_length() == 8
    assert parsed_box.get_payload() == b""
    assert end_offset == 8


def test_parse_from_with_payload():
    raw = b"\x00\x00\x00\x0c\x6a\x75\x6d\x62\x01\x02\x03\x04"

    parsed_box, end_offset = Box.parse_from_bytes(raw)

    assert parsed_box.get_type() == b"jumb".hex()
    assert parsed_box.get_length() == 12
    assert parsed_box.get_payload() == b"\x01\x02\x03\x04"
    assert end_offset == 12


def test_iter_boxes():
    raw = b"\x00\x00\x00\x08\x6a\x75\x6d\x64" + b"\x00\x00\x00\x0a\x6a\x73\x6f\x6e\x00\x00"

    boxes = list(iter_boxes(raw))

    assert len(boxes) == 2
    assert boxes[0].get_type() == b"jumd".hex()
    assert boxes[1].get_type() == b"json".hex()
    assert boxes[1].get_payload() == b"\x00\x00"


def test_parse_from_not_enough_data():
    short = b"\x00\x00\x00\x10\x6a\x75\x6d\x62"

    try:
        Box.parse_from_bytes(short)
        raise AssertionError("Should have raised")
    except ValueError:
        pass
