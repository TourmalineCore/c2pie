from c2pie.c2pa.assertion import HashDataAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes
from c2pie.utils.content_types import jumbf_content_types

CAI_OFFSET = 2
HASHED_DATA = b"\x00" * 32


def test_hash_data_assertion_has_correct_type():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.type == C2PA_AssertionTypes.data_hash


def test_hash_data_assertion_content_type_is_cbor():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.get_content_type() == jumbf_content_types["cbor"]


def test_hash_data_assertion_label():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.get_label() == "c2pa.hash.data"


def test_hash_data_assertion_schema_alg_is_sha256():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.schema["alg"] == "sha256"


def test_hash_data_assertion_schema_pad_is_16_bytes_lenght():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.schema["pad"] == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"


def test_hash_data_assertion_has_correct_offset():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.schema["exclusions"][0]["start"] == CAI_OFFSET


def test_hash_data_assertion_default_exclusion_length():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert data_hash_assertion.schema["exclusions"][0]["length"] == 0


def test_hash_data_assertion_has_correct_hash():
    expected_hashed_data = b"\xab" * 32
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=expected_hashed_data,
    )
    assert data_hash_assertion.schema["hash"] == expected_hashed_data


def test_hash_data_assertion_serializes_as_cbor():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    expected_payload = cbor_to_bytes(data_hash_assertion.schema)
    assert len(data_hash_assertion.content_boxes) == 1
    assert data_hash_assertion.content_boxes[0].payload == expected_payload


def test_hash_data_assertion_with_additional_exclusions():
    additional = [
        {
            "start": 100,
            "length": 200,
        },
    ]
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
        additional_exclusions=additional,
    )
    exclusions = data_hash_assertion.schema["exclusions"]
    assert len(exclusions) == 2
    assert exclusions[1] == {"start": 100, "length": 200}


def test_hash_data_assertion_without_additional_exclusions_has_one_exclusion():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    assert len(data_hash_assertion.schema["exclusions"]) == 1


def test_set_hash_data_length_updates_exclusion():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    data_hash_assertion.set_hash_data_length(200)
    assert data_hash_assertion.schema["exclusions"][0]["length"] == 200


def test_set_hash_data_length_updates_content_box_payload():
    data_hash_assertion = HashDataAssertion(
        cai_offset=CAI_OFFSET,
        hashed_data=HASHED_DATA,
    )
    data_hash_assertion.set_hash_data_length(200)
    expected_payload = cbor_to_bytes(data_hash_assertion.schema)
    assert data_hash_assertion.content_boxes[0].payload == expected_payload
