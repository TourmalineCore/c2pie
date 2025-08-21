from tc_c2pa_py.c2pa.assertion import Assertion
from tc_c2pa_py.c2pa.assertion_store import AssertionStore
from tc_c2pa_py.utils.assertion_schemas import C2PA_AssertionTypes
from tc_c2pa_py.utils.content_types import c2pa_content_types


def test_create_assertion_store():
    test_assertion_store = AssertionStore()

    assert test_assertion_store is not None
    assert test_assertion_store.get_content_type() == c2pa_content_types["assertions"]
    assert test_assertion_store.get_label() == "c2pa.assertions"
    assert len(test_assertion_store.content_boxes) == 0


def test_create_assertion_store_with_content():
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "tc_c2pa_py",
    }
    test_assertion = Assertion(assertion_type=C2PA_AssertionTypes.creative_work, schema=creative_work_schema)

    test_assertions = [test_assertion, test_assertion]

    test_assertion_store = AssertionStore(assertions=test_assertions)

    assert len(test_assertion_store.assertions) != 0
    assert len(test_assertion_store.content_boxes) != 0
