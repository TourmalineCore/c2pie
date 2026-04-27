from c2pie.c2pa.assertion import ActionsAssertion, Assertion, HashDataAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes, json_to_bytes
from c2pie.utils.content_types import jumbf_content_types


def test_create_assertion():
    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, {})

    assert test_assertion is not None


def test_create_assertion_with_jumbf_type():
    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, {})
    assert test_assertion.t_box == b"jumb".hex()
    assert test_assertion.get_content_type() == jumbf_content_types["json"]


def test_create_assertion_with_correct_label():
    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, {})
    assert test_assertion.get_label() == "stds.schema-org.CreativeWork"


def test_create_assertion_with_true_type():
    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, {})

    assert test_assertion.type == C2PA_AssertionTypes.creative_work


def test_create_assertion_with_thumbnail_type():
    test_assertion = Assertion(C2PA_AssertionTypes.thumbnail, {})

    assert test_assertion.get_content_type() == jumbf_content_types["codestream"]


def test_assertion_cannot_create_with_no_type():
    test_assertion = Assertion(None, {})  # type: ignore

    assert test_assertion.type not in list(C2PA_AssertionTypes)
    assert test_assertion.get_content_type() == b""


def test_create_assertion_with_correct_schema():
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }

    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

    assert test_assertion.schema == creative_work_schema


def test_serialize_json_assertion():
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }

    test_serialized_json_assertion = json_to_bytes(creative_work_schema)

    assert (
        test_serialized_json_assertion
        == b'{"@context":"https://schema.org","@type":"CreativeWork","author":[{"@type":"Person","name":"Tourmaline Core"}],"copyrightYear":"2024","copyrightHolder":"c2pie"}'  # noqa: E501
    )


def test_serialize_cbor_assertion():
    actions_schema_cbor = {"actions": [{"action": "c2pa.edited", "parameters": "gradient"}]}

    test_serialized_cbor_assertion = cbor_to_bytes(actions_schema_cbor)

    assert test_serialized_cbor_assertion == b"\xa1gactions\x81\xa2factionkc2pa.editedjparametershgradient"


def test_assertion_content_boxes_not_empty():  # noqa: F811
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }

    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

    assert len(test_assertion.content_boxes) != 0


def test_additional_extensions_adding_for_hash_data_assertions():
    additional_exclusion = {"some_extension": 343}
    test_assertion = HashDataAssertion(cai_offset=124, hashed_data=b"", additional_exclusions=[additional_exclusion])
    assert additional_exclusion in test_assertion.schema["exclusions"]


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
