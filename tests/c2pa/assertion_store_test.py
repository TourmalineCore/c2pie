from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


def test_create_assertion_store_with_no_assertions():
    assertion_store = AssertionStore(assertions=[])

    assert assertion_store is not None
    assert assertion_store.get_content_type() == c2pa_content_types["assertions"]
    assert assertion_store.get_label() == "c2pa.assertions"
    assert len(assertion_store.content_boxes) == 0


def test_create_assertion_store_with_assertions():
    actions_assertion_schema: dict[str, list[dict[str, str]]] = {"actions": [{"action": "c2pa.created"}]}
    actions_assertion_content_box = Assertion.content_box_from_schema(
        C2PA_AssertionTypes.actions, actions_assertion_schema
    )

    action_assertion = Assertion(
        assertion_type=C2PA_AssertionTypes.actions, content_boxes=actions_assertion_content_box
    )

    assertions = [action_assertion, action_assertion]

    assertion_store = AssertionStore(assertions=assertions)

    assert len(assertion_store.assertions) != 0
    assert len(assertion_store.content_boxes) != 0
