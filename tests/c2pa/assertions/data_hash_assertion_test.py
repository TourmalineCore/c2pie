import pytest

from c2pie.c2pa.assertion import HashDataAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes
from c2pie.utils.content_types import jumbf_content_types

CAI_OFFSET = 2
HASHED_DATA = b"\x00" * 32


def test_hash_data_assertion_has_correct_type():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert data_hash_assertion.type == C2PA_AssertionTypes.data_hash


def test_hash_data_assertion_content_type_is_cbor():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert data_hash_assertion.get_content_type() == jumbf_content_types["cbor"]


def test_hash_data_assertion_label():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert data_hash_assertion.get_label() == "c2pa.hash.data"


def test_hash_data_assertion_schema_alg_is_sha256():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert data_hash_assertion.schema["alg"] == "sha256"


def test_hash_data_assertion_schema_pad_is_64_bytes_lenght():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert data_hash_assertion.schema["pad"] == b"\x00" * 64


def test_hash_data_assertion_has_correct_hash():
    expected_hashed_data = b"\xab" * 32
    data_hash_assertion = HashDataAssertion(hashed_data=expected_hashed_data)
    assert data_hash_assertion.schema["hash"] == expected_hashed_data


def test_hash_data_assertion_serializes_as_cbor():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    expected_payload = cbor_to_bytes(data_hash_assertion.schema)
    assert len(data_hash_assertion.content_boxes) == 1
    assert data_hash_assertion.content_boxes[0].payload == expected_payload


# def test_hash_data_assertion_with_additional_exclusions():
#     additional = [
#         {
#             "start": 100,
#             "length": 200,
#         },
#     ]

#     data_hash_assertion = HashDataAssertion(
#         hashed_data=HASHED_DATA,
#         additional_exclusions=additional,
#     )

#     exclusions = data_hash_assertion.schema["exclusions"]

#     assert len(exclusions) == 1
#     assert exclusions[0] == {
#         "start": 100,
#         "length": 200,
#     }

# def test_additional_extensions_adding_for_hash_data_assertions():
#     additional_exclusion = {
#         "start": 100,
#         "length": 1000,
#     }

#     data_hash_assertion = HashDataAssertion(
#         hashed_data=b"",
#         additional_exclusions=[additional_exclusion],
#     )

#     assert additional_exclusion in data_hash_assertion.schema["exclusions"]


def test_hash_data_assertion_without_additional_exclusions_has_not_exclusions():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    assert len(data_hash_assertion.schema["exclusions"]) == 0


def test_set_hash_data_length_updates_exclusion():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    data_hash_assertion.add_full_c2pa_structure_exclusion(
        CAI_OFFSET,
        200,
    )
    assert data_hash_assertion.schema["exclusions"][0]["length"] == 200


def test_set_hash_data_length_updates_content_box_payload():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    data_hash_assertion.add_full_c2pa_structure_exclusion(
        CAI_OFFSET,
        200,
    )
    expected_payload = cbor_to_bytes(data_hash_assertion.schema)
    assert data_hash_assertion.content_boxes[0].payload == expected_payload


def test_align_hash_data_with_large_difference_causes_error():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    data_hash_assertion.schema["pad"] = b"\x00"

    with pytest.raises(ValueError, match="Difference in length exceeds the predefined pad"):
        data_hash_assertion.add_full_c2pa_structure_exclusion(
            CAI_OFFSET,
            200,
        )


def test_exceed_cbor_23_bytes_limit_add_1_byte_to_lenght():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)

    # Example empty list (exclusions) serialized in CBOR:
    # []
    #
    # has 1 bytes in length

    # We need to set the exclusion so that the difference
    # is less than 24 bytes:
    # current pad - x (difference) <= 23
    # ~ 64 > x >= 41 (64 - 23)

    # Example not empty list (exclusions) serialized in CBOR:
    # [
    #     {
    #         "start": 2,
    #         "length": "",
    #     }
    # ]
    #
    # has 17 bytes in length

    # not empty list - empty list = difference
    # x - 1 = 41
    # x (not empty list) = 42
    # 42 - 17 - 1 (CBOR header additional byte, because pad > 23) = 24
    fake_payload = b"\x00" * 24

    data_hash_assertion.add_full_c2pa_structure_exclusion(
        CAI_OFFSET,
        fake_payload,
    )

    # current pad - difference - additional_byte = aligned pad
    # 64 - 41 = 23 - 1 (additional_byte) = 22
    assert len(data_hash_assertion.schema["pad"]) == 22


def test_data_hash_assertion_exclusions_more_then_23():
    data_hash_assertion = HashDataAssertion(hashed_data=HASHED_DATA)
    data_hash_assertion.schema = {
        "exclusions": [{"start": 0, "length": 0}] * 23,
        "alg": "sha256",
        "hash": b"\x00\x00\x00",
        "pad": b"\x00" * 64,
    }

    data_hash_assertion.add_full_c2pa_structure_exclusion(
        CAI_OFFSET,
        0,
    )

    assert len(data_hash_assertion.schema["pad"]) == 47
