import cbor2

from c2pie.c2pa.assertion import Assertion
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


def test_create_claim_with_label():
    claim = Claim(
        manifest_label="valid_manifest_label",
        assertion_store=AssertionStore([]),
    )

    assert claim is not None
    assert claim.manifest_label == "valid_manifest_label"
    assert claim.claim_signature_label == "self#jumbf=c2pa/valid_manifest_label/c2pa.signature"


def create_claim_with_label_and_assertion_store():
    actions_assertion = Assertion(assertion_type=C2PA_AssertionTypes.actions, schema={})
    assertions = [actions_assertion, actions_assertion]

    assertion_store = AssertionStore(assertions=assertions)

    claim = Claim(
        manifest_label="valid_manifest_label",
        assertion_store=assertion_store,
    )

    assert len(claim.assertion_store.assertions) != 0


def test_create_claim_with_jumbf_type():
    actions_assertion = Assertion(assertion_type=C2PA_AssertionTypes.actions, schema={})
    assertions = [actions_assertion, actions_assertion]

    assertion_store = AssertionStore(assertions=assertions)

    claim = Claim(
        manifest_label="valid_manifest_label",
        assertion_store=assertion_store,
    )

    assert claim.t_box == b"jumb".hex()
    assert claim.get_content_type() == c2pa_content_types["claim"]
    assert claim.get_manifest_label() == "valid_manifest_label"
    assert claim.content_boxes[0].get_type() == b"cbor".hex()


def test_create_claim_with_none_as_assertion_store():
    claim = Claim(
        manifest_label="valid_manifest_label",
        assertion_store=None,
    )  # type: ignore

    payload = cbor2.loads(claim.content_boxes[0].get_payload())

    assert "assertions" not in payload.keys()
