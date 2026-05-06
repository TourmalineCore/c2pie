from c2pie.c2pa.assertion import Assertion
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.c2pa.claim_signature import ClaimSignature
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


def test_create_claim_signature_with_empty_claim():
    assertion_store = AssertionStore(assertions=[])
    claim_signature = ClaimSignature(
        claim=Claim(
            assertion_store=assertion_store,
            manifest_label="urn:c2pa:test-uuid",
            dc_title="test.jpg",
            tsa_url=None,
            require_tsa=False,
            tsa_log_dir=None,
        ),
        private_key=b"",
        certificate_pem_bundle=b"",
        certificate=None,
    )

    assert claim_signature is not None
    assert claim_signature.get_label() == "c2pa.signature"
    assert claim_signature.get_content_type() == c2pa_content_types["claim_signature"]


def test_create_claim_signature_with_non_empty_claim():
    key_filepath = "tests/credentials/private-key.pem"
    cert_filepath = "tests/credentials/certificate-chain.pub"

    with open(key_filepath, "rb") as f:
        key = f.read()

    with open(cert_filepath, "rb") as f:
        certificate = f.read()

    actions_assertion = Assertion(assertion_type=C2PA_AssertionTypes.actions, schema={})
    assertions = [actions_assertion, actions_assertion]
    assertion_store = AssertionStore(assertions=assertions)
    claim = Claim(
        manifest_label="urn:c2pa:test-uuid",
        assertion_store=assertion_store,
        dc_title="test.jpg",
    )

    claim_signature = ClaimSignature(
        claim=claim,
        private_key=key,
        certificate=certificate,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )

    assert claim_signature.claim is not None  # noqa: B015
    assert claim_signature.content_boxes[0].get_type() == b"cbor".hex()  # noqa: B015
