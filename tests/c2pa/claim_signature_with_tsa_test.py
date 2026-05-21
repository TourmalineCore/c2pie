from unittest.mock import patch

import cbor2
import pytest

from c2pie.c2pa.assertion import Assertion
from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.c2pa.claim import Claim
from c2pie.c2pa.claim_signature import ClaimSignature
from c2pie.tsa.exceptions import TSARequiredError
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes

_KEY_FILE = "tests/fixtures/credentials/private-key.pem"
_CERT_FILE = "tests/fixtures/credentials/certificate-chain.pub"
_FAKE_TST_DER = b"\x30\x82\x01\x00"


@pytest.fixture(scope="module")
def mock_private_key_and_certificate():
    with open(_KEY_FILE, "rb") as f:
        key = f.read()
    with open(_CERT_FILE, "rb") as f:
        cert = f.read()
    return key, cert


@pytest.fixture
def mock_claim():
    actions_assertion = Assertion(C2PA_AssertionTypes.actions, {})
    assertion_store = AssertionStore([actions_assertion])

    return Claim(
        manifest_label="urn:c2pa:test-uuid",
        assertion_store=assertion_store,
        dc_title="test.jpg",
    )


def _decode_cose_sign1(claim_signature: ClaimSignature):
    """Parse the COSE_Sign1 from ClaimSignature and return its four elements."""

    raw = claim_signature.content_boxes[0].get_payload()
    tagged = cbor2.loads(raw)
    protected_header, unprotected_header, payload, sig = tagged.value

    return protected_header, unprotected_header, payload, sig


def test_no_tsa_url_produces_empty_unprotected_header(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    claim_signature = ClaimSignature(
        claim=mock_claim,
        private_key=key,
        certificate_pem_bundle=cert,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )
    _, unprotected_header, _, _ = _decode_cose_sign1(claim_signature)
    assert unprotected_header == {}


def test_require_tsa_true_without_url_raises(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with pytest.raises(TSARequiredError):
        ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url=None,
            require_tsa=True,
            tsa_log_dir=None,
        )


def test_require_tsa_false_without_url_does_not_raise(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    claim_signature = ClaimSignature(
        claim=mock_claim,
        private_key=key,
        certificate_pem_bundle=cert,
        tsa_url=None,
        require_tsa=False,
        tsa_log_dir=None,
    )
    assert claim_signature is not None


def test_tsa_url_adds_sigtst2_to_unprotected_header(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER):
        claim_signature = ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=False,
            tsa_log_dir=None,
        )
    _, unprotected_header, _, _ = _decode_cose_sign1(claim_signature)
    assert "sigTst2" in unprotected_header


def test_tst_tokens_contains_one_entry(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER):
        claim_signature = ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=False,
            tsa_log_dir=None,
        )
    _, unprotected_header, _, _ = _decode_cose_sign1(claim_signature)
    tokens = unprotected_header["sigTst2"]["tstTokens"]
    assert len(tokens) == 1


def test_tst_token_val_matches_fetch_timestamp_return(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER):
        claim_signature = ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=False,
            tsa_log_dir=None,
        )
    _, unprotected_header, _, _ = _decode_cose_sign1(claim_signature)
    assert unprotected_header["sigTst2"]["tstTokens"][0]["val"] == _FAKE_TST_DER


def test_fetch_timestamp_called_with_correct_tsa_url(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    tsa_url = "http://tsa.example.com"
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER) as mock_fetch:
        ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url=tsa_url,
            require_tsa=False,
            tsa_log_dir=None,
        )
    mock_fetch.assert_called_once()
    assert mock_fetch.call_args.kwargs["tsa_url"] == tsa_url


def test_tsa_log_dir_forwarded_to_fetch_timestamp(mock_private_key_and_certificate, mock_claim, tmp_path):
    key, cert = mock_private_key_and_certificate
    log_dir = str(tmp_path / "logs")
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER) as mock_fetch:
        ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=False,
            tsa_log_dir=log_dir,
        )
    assert mock_fetch.call_args.kwargs["tsa_log_dir"] == log_dir


def test_require_tsa_true_with_valid_url_does_not_raise(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER):
        claim_signature = ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=True,
            tsa_log_dir=None,
        )
    assert claim_signature is not None


def test_cose_payload_is_detached(mock_private_key_and_certificate, mock_claim):
    """C2PA requires detached payload (None) in COSE_Sign1."""
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp", return_value=_FAKE_TST_DER):
        claim_signature = ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url="http://tsa.example.com",
            require_tsa=False,
            tsa_log_dir=None,
        )
    _, _, payload, _ = _decode_cose_sign1(claim_signature)
    assert payload is None


def test_tsa_url_none_does_not_call_fetch_timestamp(mock_private_key_and_certificate, mock_claim):
    key, cert = mock_private_key_and_certificate
    with patch("c2pie.c2pa.claim_signature.fetch_timestamp") as mock_fetch:
        ClaimSignature(
            claim=mock_claim,
            private_key=key,
            certificate_pem_bundle=cert,
            tsa_url=None,
            require_tsa=False,
            tsa_log_dir=None,
        )
    mock_fetch.assert_not_called()
