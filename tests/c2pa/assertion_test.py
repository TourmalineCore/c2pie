# Actions Assertion tests


def test_actions_assertion_content_type_is_cbor():
    test_assertion = ActionsAssertion(action="c2pa.created")
    assert test_assertion.get_content_type() == jumbf_content_types["cbor"]


def test_actions_assertion_label():
    test_assertion = ActionsAssertion(action="c2pa.created")
    assert test_assertion.get_label() == "c2pa.actions.v2"


def test_actions_assertion_schema_fields():
    test_assertion = ActionsAssertion(action="c2pa.created")
    assert test_assertion.schema["actions"][0]["action"] == "c2pa.created"


def test_actions_assertion_schema_has_no_parameters_by_default():
    assertion = ActionsAssertion(action="c2pa.created")
    assert "parameters" not in assertion.schema["actions"][0]


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

    test_assertion = ActionsAssertion(action="c2pa.opened", parameters=expected_parameters)
    assert test_assertion.schema["actions"][0]["action"] == "c2pa.opened"
    assert test_assertion.schema["actions"][0]["parameters"] == expected_parameters


def test_actions_assertion_serializes_as_cbor():
    test_assertion = ActionsAssertion(action="c2pa.created")
    expected_payload = cbor_to_bytes({"actions": [{"action": "c2pa.created"}]})
    assert len(test_assertion.content_boxes) == 1
    assert test_assertion.content_boxes[0].payload == expected_payload
