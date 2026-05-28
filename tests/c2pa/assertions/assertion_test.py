from c2pie.c2pa.assertion import Assertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes, json_to_bytes
from c2pie.utils.content_types import jumbf_content_types


def test_create_assertion():
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assert actions_assertion is not None


def test_create_assertion_with_jumbf_type():
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assert actions_assertion.t_box == b"jumb".hex()
    assert actions_assertion.get_content_type() == jumbf_content_types["cbor"]


def test_create_assertion_with_correct_label():
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assert actions_assertion.get_label() == "c2pa.actions.v2"


def test_create_assertion_with_true_type():
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assert actions_assertion.type == C2PA_AssertionTypes.actions


def test_assertion_cannot_create_with_no_type():
    assertion = Assertion(None, {})  # type: ignore
    assert assertion.type not in list(C2PA_AssertionTypes)
    assert assertion.get_content_type() == b""


def test_create_assertion_with_correct_schema():
    actions_assertion_schema: dict[str, list[dict[str, str]]] = {
        "actions": [
            {
                "action": "c2pa.created",
            },
        ],
    }

    actions_assertion = Assertion(C2PA_AssertionTypes.actions, actions_assertion_schema)

    assert actions_assertion.schema == actions_assertion_schema


def test_serialize_json_assertion():
    actions_schema_json = {
        "actions": [
            {
                "action": "c2pa.created",
            },
        ],
    }

    result = json_to_bytes(actions_schema_json)

    assert result == b'{"actions":[{"action":"c2pa.created"}]}'


def test_serialize_cbor_assertion():
    actions_schema_cbor = {
        "actions": [
            {
                "action": "c2pa.edited",
                "parameters": "gradient",
            },
        ],
    }

    test_serialized_cbor_actions_assertion = cbor_to_bytes(actions_schema_cbor)

    assert test_serialized_cbor_actions_assertion == b"\xa1gactions\x81\xa2factionkc2pa.editedjparametershgradient"


def test_assertion_content_boxes_not_empty():  # noqa: F811
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assert len(actions_assertion.content_boxes) != 0
