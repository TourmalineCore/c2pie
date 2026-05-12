from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from c2pie.tsa.client import _build_request, fetch_timestamp
from c2pie.tsa.exceptions import TSAConnectionError, TSAResponseError

_FAKE_TST_DER = b"\x30\x82\x01\x00"


def _mock_make_http_response(content: bytes = b"TimeStampResp") -> MagicMock:
    """Return a mock decoded TimeStampResp with status=0 (granted)."""

    mock = MagicMock()
    mock.content = content
    mock.raise_for_status.return_value = None
    return mock


def _mock_make_granted_asn1_resp(token_has_value: bool = True) -> MagicMock:
    """Return a mock decoded TimeStampResp with status=0 (granted)."""

    mock_resp = MagicMock()
    mock_resp["status"]["status"].__int__.return_value = 0
    mock_resp["timeStampToken"].hasValue.return_value = token_has_value
    return mock_resp


def _mock_make_rejected_asn1_resp() -> MagicMock:
    """Return a mock decoded TimeStampResp with status=2 (rejected)."""

    mock_resp = MagicMock()
    mock_resp["status"]["status"].__int__.return_value = 2
    return mock_resp


class TestBuildRequest:
    def test_returns_bytes_and_int_nonce(self):
        time_stamp_req_der, nonce = _build_request(b"test_input")
        assert isinstance(time_stamp_req_der, bytes)
        assert len(time_stamp_req_der) > 0
        assert isinstance(nonce, int)

    def test_nonce_is_within_64_bits(self):
        _, nonce = _build_request(b"test_input")
        assert 0 <= nonce < 2**64

    def test_different_inputs_produce_different_der(self):
        time_stamp_req_der1, _ = _build_request(b"input_one")
        time_stamp_req_der2, _ = _build_request(b"input_two")
        assert time_stamp_req_der1 != time_stamp_req_der2

    def test_same_input_different_nonces(self):
        _, nonce1 = _build_request(b"input_one")
        _, nonce2 = _build_request(b"input_one")
        assert nonce1 != nonce2


class TestFetchTimestampSuccess:
    def test_returns_encoded_token_bytes(self):
        expected_token = b"timestamp_der_encoded_token"

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=expected_token),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            actual_token = fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=None,
            )

        assert actual_token == expected_token

    def test_sends_post_to_tsa_url(self):
        tsa_url = "http://tsa.example.com"

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode"),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=None,
            )

        call_args = mock_post.call_args
        assert call_args.kwargs.get("url") == tsa_url

    def test_sends_timestamp_query_content_type(self):
        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode"),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=None,
            )

        headers = mock_post.call_args.kwargs.get("headers")
        assert headers.get("Content-Type") == "application/timestamp-query"

    def test_uses_30_second_timeout(self):
        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode"),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=None,
            )

        assert mock_post.call_args.kwargs.get("timeout") == 30


class TestFetchTimestampErrors:
    def test_connection_error_raises_tsa_connection_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("refused")

            with pytest.raises(TSAConnectionError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )

    def test_timeout_raises_tsa_connection_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("timed out")

            with pytest.raises(TSAConnectionError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )

    def test_http_error_status_raises_tsa_connection_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post:
            mock_resp = _mock_make_http_response()
            mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
            mock_post.return_value = mock_resp

            with pytest.raises(TSAConnectionError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )

    def test_unparseable_response_raises_tsa_response_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post, patch("c2pie.tsa.client.decoder.decode") as mock_decode:
            mock_post.return_value = _mock_make_http_response()
            mock_decode.side_effect = Exception("ASN.1 parse error")

            with pytest.raises(TSAResponseError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )

    def test_rejection_status_raises_tsa_response_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post, patch("c2pie.tsa.client.decoder.decode") as mock_decode:
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_rejected_asn1_resp(), b"")

            with pytest.raises(TSAResponseError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )

    def test_granted_without_token_raises_tsa_response_error(self):
        with patch("c2pie.tsa.client.http.post") as mock_post, patch("c2pie.tsa.client.decoder.decode") as mock_decode:
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(token_has_value=False), b"")

            with pytest.raises(TSAResponseError):
                fetch_timestamp(
                    signature_bytes=b"signature",
                    tsa_url="http://tsa.example.com",
                    tsa_log_dir=None,
                )


class TestFetchTimestampLogging:
    def test_log_dir_creates_request_and_response_files(self, tmp_path):
        log_dir = tmp_path / "tsa_logs"

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=_FAKE_TST_DER),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=str(log_dir),
            )

        files = list(log_dir.iterdir())
        names = {f.name for f in files}

        assert len(files) == 2
        assert any("request.der" in name for name in names)
        assert any("response.der" in name for name in names)

    def test_log_files_share_timestamp_nonce_prefix(self, tmp_path):
        log_dir = tmp_path / "logs"

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=_FAKE_TST_DER),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=str(log_dir),
            )

        files = sorted(file.name for file in log_dir.iterdir())
        prefix_a = files[0].rsplit("_", 1)[0]
        prefix_b = files[1].rsplit("_", 1)[0]

        assert prefix_a == prefix_b

    def test_response_bytes_written_to_log(self, tmp_path):
        log_dir = tmp_path / "logs"
        response_content = b"raw_tsa_response_content"

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=_FAKE_TST_DER),
        ):
            mock_post.return_value = _mock_make_http_response(content=response_content)
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=str(log_dir),
            )

        response_files = [file for file in log_dir.iterdir() if "response" in file.name]

        assert response_files[0].read_bytes() == response_content

    def test_no_log_dir_creates_no_files(self, tmp_path):
        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=_FAKE_TST_DER),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=None,
            )

        assert list(tmp_path.iterdir()) == []

    def test_log_dir_is_created_if_missing(self, tmp_path):
        nested_log_dir = tmp_path / "a" / "b" / "tsa_logs"
        assert not nested_log_dir.exists()

        with (
            patch("c2pie.tsa.client.http.post") as mock_post,
            patch("c2pie.tsa.client.decoder.decode") as mock_decode,
            patch("c2pie.tsa.client.encoder.encode", return_value=_FAKE_TST_DER),
        ):
            mock_post.return_value = _mock_make_http_response()
            mock_decode.return_value = (_mock_make_granted_asn1_resp(), b"")

            fetch_timestamp(
                signature_bytes=b"signature",
                tsa_url="http://tsa.example.com",
                tsa_log_dir=str(nested_log_dir),
            )

        assert nested_log_dir.exists()
