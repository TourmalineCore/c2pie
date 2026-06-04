import re
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from c2pie.signing import _read_and_check_size_of_thumbnail_file, sign_file
from c2pie.utils.generate_hashed_uri_map import generate_hashed_uri_map

TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"


def test_generate_hashed_uri_map_required_fields():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
    )
    assert hash_uri_map["url"] == "self#jumbf=c2pa.assertions/c2pa.ingredient.v3"
    assert hash_uri_map["hash"] == b"\x01\x02\x03"


def test_generate_hashed_uri_map_no_alg_by_default():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
    )
    assert "alg" not in hash_uri_map


def test_generate_hashed_uri_map_with_alg():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
        hash_algorithm="sha256",
    )
    assert hash_uri_map["alg"] == "sha256"


def test_attempt_to_read_large_thumbnail_file_caused_error():
    oversized_bytes = b"\x00" * (1024 * 1024 + 1)

    with patch("builtins.open", mock_open(read_data=oversized_bytes)):
        with pytest.raises(
            ValueError,
            match="The thumbnail file is too large! The size must not exceed 1024x1024. Recommended 512x512.",
        ):
            _read_and_check_size_of_thumbnail_file(Path("thumbnail.jpg"))


def test_read_thumbnail_file_within_size_limit():
    valid_bytes = b"\x00" * (1024 * 1024)

    with patch("builtins.open", mock_open(read_data=valid_bytes)):
        result = _read_and_check_size_of_thumbnail_file(Path("thumbnail.jpg"))

    assert result == valid_bytes


def test_calling_sign_file_with_thumbnail_in_unsupported_format_causes_error():
    expected_error_message = (
        "The thumbnail file has an incorrect extension: .pdf. "
        "Currently, only the following extensions are supported: ['.jpeg', '.jpg', '.png']"
    )

    with patch("c2pie.signing._load_certificates_and_key", return_value=(b"key", b"cert")):
        with pytest.raises(
            ValueError,
            match=re.escape(expected_error_message),
        ):
            sign_file(
                input_path=TEST_FILES_DIR / "test_image.jpg",
                thumbnail_file_path=TEST_FILES_DIR / "test_doc.pdf",
            )
