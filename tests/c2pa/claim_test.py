from c2pie.c2pa.assertion import Assertion
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


def test_create_claim_with_label():
    test_claim = Claim(
        claim_generator="c2pie", manifest_label="valid_manifest_label", assertion_store=AssertionStore([])
    )

    assert test_claim is not None
    assert test_claim.claim_generator == "c2pie"
    assert test_claim.manifest_label == "valid_manifest_label"
    assert test_claim.claim_signature_label == "self#jumbf=c2pa/valid_manifest_label/c2pa.signature"


def test_create_claim_with_label_and_assertion_store():
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }
    test_assertion = Assertion(assertion_type=C2PA_AssertionTypes.creative_work, schema=creative_work_schema)

    test_assertions = [test_assertion, test_assertion]

    test_assertion_store = AssertionStore(assertions=test_assertions)

    test_claim = Claim(
        claim_generator="c2pie", manifest_label="valid_manifest_label", assertion_store=test_assertion_store
    )

    assert len(test_claim.assertion_store.assertions) != 0


def test_create_claim_with_jumbf_type():
    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }
    test_assertion = Assertion(assertion_type=C2PA_AssertionTypes.creative_work, schema=creative_work_schema)

    test_assertions = [test_assertion, test_assertion]

    test_assertion_store = AssertionStore(assertions=test_assertions)

    test_claim = Claim(
        claim_generator="c2pie", manifest_label="valid_manifest_label", assertion_store=test_assertion_store
    )

    assert test_claim.t_box == b"jumb".hex()
    assert test_claim.get_content_type() == c2pa_content_types["claim"]
    assert test_claim.content_boxes[0].get_type() == b"cbor".hex()
