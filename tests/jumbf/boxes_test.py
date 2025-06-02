import pytest

from tc_c2pa_py.jumbf_boxes.box import Box


def test_create_box():

    test_box = Box('jumb'.encode('utf-8').hex())

    assert test_box.t_box == 'jumb'.encode('utf-8').hex()


def test_get_some_box_length():

    test_box = Box('jumb'.encode('utf-8').hex())

    assert test_box.get_length() != None


def test_get_true_box_length():

    test_box = Box('jumb'.encode('utf-8').hex())

    assert test_box.get_length() == 8


def test_get_box_type():

    test_box = Box('jumb'.encode('utf-8').hex())

    assert test_box.get_type() == 'jumb'.encode('utf-8').hex()


def test_serialize_box():

    expected_serialized_data = b'\x00\x00\x00\x08\x6a\x75\x6d\x62'

    test_box = Box('jumb'.encode('utf-8').hex())

    assert test_box.serialize() == expected_serialized_data

