from c2pie.c2pa_parsing.jpg_reader import extract_manifest_store_bytes, extract_raw_image_bytes
from c2pie.c2pa_injection.jpg_injection import JpgSegmentApp11Storage
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


_SOI = b"\xFF\xD8"
_EOI = b"\xFF\xD9"
_FAKE_IMAGE_DATA = b"\xFF\xE0" + b"\x00\x10" + b"\x00" * 14  # APP0 segment


def _make_store_bytes() -> bytes:
    from c2pie.jumbf_boxes.content_box import ContentBox

    manifest = SuperBox(
        content_type=c2pa_content_types["default_manifest"],
        label="urn:uuid:test-manifest",
        content_boxes=[ContentBox(box_type=b"cbor".hex(), payload=b"cbor-data")],
    )
    store = SuperBox(
        content_type=c2pa_content_types["manifest_store"],
        label="c2pa",
        content_boxes=[manifest],
    )
    return store.serialize()


def _make_jpg_with_c2pa() -> bytes:
    store_bytes = _make_store_bytes()
    storage = JpgSegmentApp11Storage(
        app11_segment_box_length=int.from_bytes(store_bytes[:4], "big"),
        app11_segment_box_type=store_bytes[4:8].decode("ascii"),
        payload=store_bytes,
    )
    app11 = storage.serialize()
    return _SOI + app11 + _FAKE_IMAGE_DATA + _EOI


def _make_plain_jpg() -> bytes:
    return _SOI + _FAKE_IMAGE_DATA + _EOI


def test_extract_store_bytes_returns_none_without_c2pa():
    jpg = _make_plain_jpg()
    assert extract_manifest_store_bytes(jpg) is None


def test_extract_store_bytes_returns_bytes_with_c2pa():
    jpg = _make_jpg_with_c2pa()
    result = extract_manifest_store_bytes(jpg)
    assert result is not None
    assert result[4:8] == b"jumb"


def test_extract_store_bytes_matches_original_store():
    store_bytes = _make_store_bytes()
    storage = JpgSegmentApp11Storage(
        app11_segment_box_length=int.from_bytes(store_bytes[:4], "big"),
        app11_segment_box_type=store_bytes[4:8].decode("ascii"),
        payload=store_bytes,
    )
    jpg = _SOI + storage.serialize() + _FAKE_IMAGE_DATA + _EOI
    result = extract_manifest_store_bytes(jpg)
    assert result == store_bytes


def test_extract_store_bytes_non_jp_app11_ignored():
    # APP11 with CI != JP should not be detected as C2PA
    fake_app11 = b"\xFF\xEB" + b"\x00\x0C" + b"XX" + b"\x00\x01" + b"\x00\x00\x00\x01" + b"\xAB\xCD"
    jpg = _SOI + fake_app11 + _EOI
    assert extract_manifest_store_bytes(jpg) is None


def test_extract_raw_image_no_c2pa_unchanged():
    jpg = _make_plain_jpg()
    assert extract_raw_image_bytes(jpg) == jpg


def test_extract_raw_image_strips_app11():
    jpg = _make_jpg_with_c2pa()
    result = extract_raw_image_bytes(jpg)
    assert result == _make_plain_jpg()


def test_extract_raw_image_preserves_soi():
    jpg = _make_jpg_with_c2pa()
    result = extract_raw_image_bytes(jpg)
    assert result[:2] == _SOI


def test_extract_raw_image_preserves_other_segments():
    store_bytes = _make_store_bytes()
    storage = JpgSegmentApp11Storage(
        app11_segment_box_length=int.from_bytes(store_bytes[:4], "big"),
        app11_segment_box_type=store_bytes[4:8].decode("ascii"),
        payload=store_bytes,
    )
    app11 = storage.serialize()
    extra_app0 = b"\xFF\xE0" + b"\x00\x10" + b"\x00" * 14
    jpg = _SOI + app11 + extra_app0 + _EOI
    result = extract_raw_image_bytes(jpg)
    assert extra_app0 in result
    assert app11 not in result
