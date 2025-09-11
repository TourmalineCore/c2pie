from c2pie.jumbf_boxes.box import Box


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
