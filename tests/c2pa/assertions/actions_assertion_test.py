from c2pie.c2pa.assertions.actions_assertion import ActionsAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes
from c2pie.utils.content_types import jumbf_content_types


def test_actions_assertion_has_correct_type():
    actions_assertion = ActionsAssertion(action="c2pa.created")
    assert actions_assertion.type == C2PA_AssertionTypes.actions


def test_actions_assertion_content_type_is_cbor():
    actions_assertion = ActionsAssertion(action="c2pa.created")
    assert actions_assertion.get_content_type() == jumbf_content_types["cbor"]


def test_actions_assertion_label():
    actions_assertion = ActionsAssertion(action="c2pa.created")
    assert actions_assertion.get_label() == "c2pa.actions.v2"


def test_actions_assertion_schema_fields():
    actions_assertion = ActionsAssertion(action="c2pa.created")
    assert actions_assertion.schema["actions"][0]["action"] == "c2pa.created"


def test_actions_assertion_schema_has_no_parameters_by_default():
    actions_assertion = ActionsAssertion(action="c2pa.created")
    assert "parameters" not in actions_assertion.schema["actions"][0]


def test_actions_assertion_schema_fields_with_parameters():
    expected_parameters = {
        "ingredients": [
            {
                "url": "self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
                "alg": "sha256",
                "hash": "B-X0kqzQsdIOC9ZxU7M/FRaaLlQ8Ap1U95//TucEjkT=",
            }
        ]
    }

    actions_assertion = ActionsAssertion(action="c2pa.opened", parameters=expected_parameters)
    assert actions_assertion.schema["actions"][0]["action"] == "c2pa.opened"
    assert actions_assertion.schema["actions"][0]["parameters"] == expected_parameters


def test_actions_assertion_serializes_as_cbor():
    actions_assertion = ActionsAssertion(action="c2pa.created")

    expected_payload = cbor_to_bytes(
        {
            "actions": [
                {
                    "action": "c2pa.created",
                },
            ],
        },
    )

    assert len(actions_assertion.content_boxes) == 1
    assert actions_assertion.content_boxes[0].payload == expected_payload
