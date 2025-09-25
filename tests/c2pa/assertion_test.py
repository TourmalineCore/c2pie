from c2pie.c2pa.assertion import Assertion
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


def test_serialize_json_assertion():  # noqa: F811
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }

    test_assertion = Assertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

    assert len(test_assertion.content_boxes) != 0
