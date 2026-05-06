from __future__ import annotations

import struct
from pathlib import Path

import pytest

from c2pie.c2pa_parsing.jpeg_parsing import extract_manifest_store_bytes_from_jpeg


def make_app11(en: int, z: int, fragment: bytes) -> bytes:
    payload = b"JP" + struct.pack(">HI", en, z) + fragment
    seg_len = len(payload) + 2
    return b"\xff\xeb" + struct.pack(">H", seg_len) + payload


def make_jpeg(*app11_segments: bytes) -> bytes:
    return b"\xff\xd8" + b"".join(app11_segments) + b"\xff\xd9"


C2PA_MARK = b"urn:c2pa:"
JUMBF = b"jumbf_box_data"
STORE = C2PA_MARK + JUMBF

EXPECTED_ACTIVE_URN = "urn:c2pa:active-manifest-label"

@pytest.fixture
def signed_jpg_bytes() -> bytes:
    path = Path(__file__).parent.parent / "test_files" / "big_c2pa_test_image.jpg"
    return path.read_bytes()

class TestJpegManifestExtractor:
    def test_extracts_something(self):
        result = extract_manifest_store_bytes_from_jpeg(make_jpeg(make_app11(1, 1, STORE)))
        assert result is not None
        assert len(result) > 0

    def test_returns_none_without_c2pa(self):
        result = extract_manifest_store_bytes_from_jpeg(make_jpeg())
        assert result is None

    def test_returns_none_for_empty_bytes(self):
        result = extract_manifest_store_bytes_from_jpeg(b"")
        assert result is None

    def test_app11_without_jp_prefix_ignored(self):
        payload = b"XX" + struct.pack(">HI", 1, 1) + STORE
        seg_len = len(payload) + 2
        seg = b"\xff\xeb" + struct.pack(">H", seg_len) + payload
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(seg)) is None

    def test_app11_without_c2pa_mark_ignored(self):
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(make_app11(1, 1, b"jumbf_box_data_only"))) is None

    def test_other_app_markers_ignored(self):
        exif = b"\xff\xe1\x00\x0aExif\x00\x00"
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(exif)) is None

    def test_binary_data_preserved(self):
        data = STORE + bytes(range(256))
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(make_app11(1, 1, data))) == data


class TestFragmentedApp11:
    def test_two_fragments_assembled_in_order(self):
        part1 = C2PA_MARK + b"first_"
        part2 = b"second"
        segs = make_jpeg(make_app11(1, 1, part1), make_app11(1, 2, part2))
        assert extract_manifest_store_bytes_from_jpeg(segs) == part1 + part2

    def test_fragments_sorted_by_z_not_file_order(self):
        part1 = C2PA_MARK + b"AAA"
        part2 = b"BBB"
        segs = make_jpeg(make_app11(1, 2, part2), make_app11(1, 1, part1))
        assert extract_manifest_store_bytes_from_jpeg(segs) == part1 + part2

    def test_many_fragments_assembled(self):
        chunks = [C2PA_MARK] + [bytes([i] * 100) for i in range(10)]
        segs = make_jpeg(*[make_app11(1, z + 1, chunk) for z, chunk in enumerate(chunks)])
        assert extract_manifest_store_bytes_from_jpeg(segs) == b"".join(chunks)


class TestMultipleStores:
    def test_returns_last_store_by_file_position(self):
        first = make_app11(1, 1, C2PA_MARK + b"first_store")
        second = make_app11(2, 1, C2PA_MARK + b"second_store")
        result = extract_manifest_store_bytes_from_jpeg(make_jpeg(first, second))
        assert result == C2PA_MARK + b"second_store"

    def test_non_c2pa_store_does_not_replace_c2pa(self):
        c2pa_seg = make_app11(1, 1, STORE)
        other_seg = make_app11(2, 1, b"other non-c2pa jumbf")
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(c2pa_seg, other_seg)) == STORE

    def test_raw_jpeg_with_two_stores_contains_two_ffeb(self):
        first = make_app11(1, 1, C2PA_MARK + b"first_store")
        second = make_app11(2, 1, C2PA_MARK + b"second_store")
        jpeg = make_jpeg(first, second)
        assert jpeg.count(b"\xff\xeb") >= 2


class TestEdgeCases:
    def test_ffeb_lookalike_does_not_crash(self):
        garbage = b"\xff\xeb\x00\x05junk"
        real_seg = make_app11(1, 1, STORE)
        jpeg = b"\xff\xd8" + garbage + real_seg + b"\xff\xd9"
        assert extract_manifest_store_bytes_from_jpeg(jpeg) == STORE

    def test_truncated_segment_does_not_crash(self):
        seg = make_app11(1, 1, STORE)[:-5]
        result = extract_manifest_store_bytes_from_jpeg(b"\xff\xd8" + seg + b"\xff\xd9")
        assert result is None or isinstance(result, bytes)

    def test_ffeb_inside_payload_not_double_counted(self):
        data = STORE + b"\xff\xeb\x00\x05extra"
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg(make_app11(1, 1, data))) == data


class TestRealFile:
    def test_extracts_something(self, signed_jpg_bytes: bytes):
        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        assert result is not None
        assert len(result) > 0

    def test_extracted_is_valid_jumbf(self, signed_jpg_bytes: bytes):
        from c2pie.jumbf_boxes.box import Box
        from c2pie.jumbf_boxes.constants import JUMB_TYPE

        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        first_box, _ = Box.parse_from_bytes(result, 0)
        assert first_box.get_type() == JUMB_TYPE

    def test_extracted_is_manifest_store(self, signed_jpg_bytes: bytes):
        from c2pie.jumbf_boxes.box import Box, iter_boxes
        from c2pie.jumbf_boxes.constants import JUMD_TYPE

        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        first_box, _ = Box.parse_from_bytes(result, 0)
        children = list(iter_boxes(first_box.get_payload()))

        assert len(children) > 0
        assert children[0].get_type() == JUMD_TYPE

    def test_result_size_matches_jumbf_lbox(self, signed_jpg_bytes: bytes):
        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        lbox = int.from_bytes(result[:4], "big")
        if lbox == 1:
            xlbox = int.from_bytes(result[8:16], "big")
            assert len(result) >= xlbox
        else:
            assert len(result) >= lbox
