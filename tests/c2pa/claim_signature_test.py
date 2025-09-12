from c2pie.c2pa.assertion import Assertion
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.c2pa.claim_signature import ClaimSignature
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


def test_create_claim_signature_with_empty():
    assertion_store = AssertionStore(assertions=[])
    test_claim_signature = ClaimSignature(
        claim=Claim(assertion_store=assertion_store), private_key=b"", certificate_pem_bundle=b"", certificate=None
    )

    assert test_claim_signature is not None
    assert test_claim_signature.get_label() == "c2pa.signature"
    assert test_claim_signature.get_content_type() == c2pa_content_types["claim_signature"]


def test_create_claim_signature_with_claim():
    key_filepath = "tests/fixtures/crypto/ps256.pem"
    cert_filepath = "tests/fixtures/crypto/ps256.pub"

    with open(key_filepath, "rb") as f:
        key = f.read()
    
    with open(cert_filepath, "rb") as f:
        certificate = f.read()

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

    test_claim_signature = ClaimSignature(claim=test_claim, private_key=key, certificate=certificate)

    assert test_claim_signature.claim is not None  # noqa: B015
    assert test_claim_signature.content_boxes[0].get_type() == b"cbor".hex()  # noqa: B015
