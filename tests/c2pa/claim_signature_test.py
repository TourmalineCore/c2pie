import cbor2
import pytest

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
        ),
        private_key=b"",
        certificate_pem_bundle=b"",
        certificate=None,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
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


def test_serialization_cose_sign1_is_performed_with_alignment():
    claim_signature = ClaimSignature.__new__(ClaimSignature)
    claim_signature.serialized_cose_sign1_length = 0

    cose_sign1 = [
        "protected_header",
        {
            "pad": b"\x00\x00\x00\x00",
        },
        "payload",
        "signature",
    ]

    serialized_cose_sign1_cbor_1 = claim_signature.serialize_cose_sign1_tagged_with_alignment(cose_sign1)

    assert claim_signature.serialized_cose_sign1_length != 0
    assert cbor2.loads(serialized_cose_sign1_cbor_1).value[1]["pad"] == cose_sign1[1]["pad"]

    cose_sign1 = [
        "protected_header",
        {
            "pad": b"\x00\x00\x00\x00",
        },
        "payload",
        "signature2",
    ]

    serialized_cose_sign1_cbor_2 = claim_signature.serialize_cose_sign1_tagged_with_alignment(cose_sign1)

    assert len(serialized_cose_sign1_cbor_1) == len(serialized_cose_sign1_cbor_2)

    cose_sign1 = [
        "protected_header",
        {
            "pad": b"\x00\x00\x00\x00",
        },
        "",
        "signature",
    ]

    serialized_cose_sign1_cbor_3 = claim_signature.serialize_cose_sign1_tagged_with_alignment(cose_sign1)

    assert len(serialized_cose_sign1_cbor_1) == len(serialized_cose_sign1_cbor_3)


def test_align_cose_sign1_with_large_difference_causes_error():
    claim_signature = ClaimSignature.__new__(ClaimSignature)
    claim_signature.serialized_cose_sign1_length = 1

    cose_sign1 = [
        "protected_header",
        {
            "pad": b"\x00\x00\x00\x00",
        },
        "payload",
        "signature",
    ]

    with pytest.raises(ValueError, match="Difference in length exceeds the predefined pad"):
        claim_signature.serialize_cose_sign1_tagged_with_alignment(cose_sign1)


def test_check():
    claim_signature = ClaimSignature.__new__(ClaimSignature)
    claim_signature.serialized_cose_sign1_length = 0

    cose_sign1 = [
        "protected_header",
        {
            "pad": b"\x00\x00\x00\x00",
        },
        "payload",
        "signature",
    ]

    serialized_cose_sign1_cbor = claim_signature.serialize_cose_sign1_tagged_with_alignment(cose_sign1)

    assert cbor2.loads(serialized_cose_sign1_cbor).tag == 18
