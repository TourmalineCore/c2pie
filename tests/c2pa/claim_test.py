import pytest

from tc_c2pa_py.c2pa.claim import Claim
from tc_c2pa_py.c2pa.assertion import Assertion
from tc_c2pa_py.c2pa.assertion_store import AssertionStore
from tc_c2pa_py.utils.content_types import c2pa_content_types, jumbf_content_types
from tc_c2pa_py.utils.assertion_schemas import C2PA_AssertionTypes

def test_create_claim_with_label():

    test_claim = Claim(claim_generator='tc_c2pa_py', manifest_label='valid_manifest_label', assertion_store=None)

    assert test_claim != None
    assert test_claim.claim_generator == 'tc_c2pa_py'
    assert test_claim.manifest_label == 'valid_manifest_label'
    assert test_claim.claim_signature_label == 'self#jumbf=c2pa/valid_manifest_label/c2pa.signature'


def test_create_claim_with_assertion_store():

    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [
            {
                "@type": "Person",
                "name": "Tourmaline Core"
            }
        ],
        "copyrightYear": "2024",
        "copyrightHolder": "tc_c2pa_py"
    }
    test_assertion = Assertion(assertion_type=C2PA_AssertionTypes.creative_work, schema=creative_work_schema)

    test_assertions = [test_assertion, test_assertion]

    test_assertion_store = AssertionStore(assertions=test_assertions)

    test_claim = Claim(claim_generator='tc_c2pa_py', manifest_label='valid_manifest_label', assertion_store=test_assertion_store)

    assert len(test_claim.assertion_store.assertions) != 0


def test_create_claim_with_jumbf_type():

    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [
            {
                "@type": "Person",
                "name": "Tourmaline Core"
            }
        ],
        "copyrightYear": "2024",
        "copyrightHolder": "tc_c2pa_py"
    }
    test_assertion = Assertion(assertion_type=C2PA_AssertionTypes.creative_work, schema=creative_work_schema)

    test_assertions = [test_assertion, test_assertion]

    test_assertion_store = AssertionStore(assertions=test_assertions)

    test_claim = Claim(claim_generator='tc_c2pa_py', manifest_label='valid_manifest_label', assertion_store=test_assertion_store)

    assert test_claim.t_box == 'jumb'.encode('utf-8').hex()
    assert test_claim.get_content_type() == c2pa_content_types["claim"]
    assert test_claim.content_boxes[0].get_type() == 'cbor'.encode('utf-8').hex()
    