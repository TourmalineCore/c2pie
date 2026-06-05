import struct
from pathlib import Path

import pytest

from c2pie.c2pa_parsing.jumbf_parsing import (
    find_box_by_label,
    get_active_manifest_uuid,
    jumd_label,
)
from c2pie.c2pa_parsing.manifest_extractor import (
    extract_manifest_store_bytes,
    extract_manifest_store_bytes_and_ranges_from_jpeg,
    extract_manifest_store_bytes_and_ranges_from_pdf,
)
from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import JUMB_TYPE, JUMD_TYPE
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.signing import _get_content_type_by_filepath
from c2pie.utils.content_types import C2PA_ContentTypes
from tests.helpers.jumbf_generators import _mock_make_app11, _mock_make_jpeg

C2PA_MARK = b"urn:c2pa:"
JUMBF = b"jumbf_box_data"
STORE = C2PA_MARK + JUMBF

EXPECTED_ACTIVE_UUID = "urn:uuid:712065da7bda430f8e425d2772b0a0b7"


@pytest.fixture
def signed_jpg_bytes() -> bytes:
    path = Path(__file__).parent.parent / "test_files" / "big_c2pa_test_image.jpg"

    return path.read_bytes()


@pytest.fixture
def signed_pdf_bytes() -> bytes:
    path = Path(__file__).parent.parent / "test_files" / "signed_signed_test_doc.pdf"

    return path.read_bytes()


class TestManifestExtractor:
    def test_get_content_type_by_pdf_filepath(self):
        result = _get_content_type_by_filepath(Path("doc.pdf"))

        assert result == C2PA_ContentTypes.pdf

    def test_get_content_type_by_jpg_filepath(self):
        result = _get_content_type_by_filepath(Path("image.jpg"))

        assert result == C2PA_ContentTypes.jpg

    def test_get_content_type_by_jpeg_filepath(self):
        result = _get_content_type_by_filepath(Path("image.jpeg"))

        assert result == C2PA_ContentTypes.jpeg

    def test_extract_manifest_store_bytes_dispatches_pdf(self, tmp_path: Path):
        pdf_bytes = (
            b"%PDF-1.7\n"
            b"<< /Type /EmbeddedFile /Subtype /application#2Fc2pa /Length 15 >>\n"
            b"stream\n"
            b"urn:c2pa:pdf!!\n"
            b"endstream\n"
        )
        path = tmp_path / "sample.pdf"
        path.write_bytes(pdf_bytes)

        result, ranges = extract_manifest_store_bytes(
            _get_content_type_by_filepath(path),
            pdf_bytes,
        )

        assert result == b"urn:c2pa:pdf!!\n"
        assert ranges == []

    def test_extract_manifest_store_bytes_dispatches_jpeg(self, tmp_path: Path):
        jpeg_bytes = _mock_make_jpeg(_mock_make_app11(1, 1, STORE))
        path = tmp_path / "sample.jpg"
        path.write_bytes(jpeg_bytes)

        result, ranges = extract_manifest_store_bytes(_get_content_type_by_filepath(path), jpeg_bytes)

        assert result == STORE
        assert ranges == [
            (
                2,
                2 + len(_mock_make_app11(1, 1, STORE)),
            ),
        ]

    def test_unsupported_extension_raises(self):
        with pytest.raises(ValueError):
            _get_content_type_by_filepath(Path("file.png"))


class TestJpegManifestExtractor:
    def test_extracts_something(self):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(
                _mock_make_app11(1, 1, STORE),
            ),
        )

        assert result is not None
        assert len(result) > 0

    def test_returns_none_without_c2pa(self):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(_mock_make_jpeg())

        assert result is None

    def test_returns_none_for_empty_bytes(self):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(b"")

        assert result is None

    def test_app11_without_jp_prefix_ignored(self):
        payload = b"XX" + struct.pack(">HI", 1, 1) + STORE
        seg_len = len(payload) + 2
        seg = b"\xff\xeb" + struct.pack(">H", seg_len) + payload

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(_mock_make_jpeg(seg))

        assert result is None

    def test_app11_without_c2pa_mark_ignored(self):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(_mock_make_app11(1, 1, b"jumbf_box_data_only"))
        )

        assert result is None

    def test_other_app_markers_ignored(self):
        exif = b"\xff\xe1\x00\x0aExif\x00\x00"
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(_mock_make_jpeg(exif))

        assert result is None

    def test_binary_data_preserved(self):
        data = STORE + bytes(range(256))

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(
                _mock_make_app11(1, 1, data),
            ),
        )

        assert result == data


class TestFragmentedApp11:
    def test_z1_segment_data_starts_at_byte_8_of_payload(self):
        # For Z = 1 the full payload[8:] is the JUMBF data —
        # LBox + TBox are included as-is, they are not a duplicated prefix here.
        data = C2PA_MARK + b"AAA"

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(
                _mock_make_app11(1, 1, data),
            ),
        )

        assert result == data

    def test_z_greater_than_1_skips_lbox_tbox_prefix(self):
        part1 = C2PA_MARK + b"AAA"
        part2 = b"BBB"

        # For Z > 1 the first 8 bytes after CI + EN + Z are the repeated LBox + TBox prefix
        # and must be stripped; only bytes[16:] contain the continuation data.
        lbox_tbox = part1[:8]

        segs = _mock_make_jpeg(
            _mock_make_app11(1, 1, part1),
            _mock_make_app11(1, 2, lbox_tbox + part2),
        )

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(segs)

        assert result == part1 + part2

    def test_fragments_sorted_by_z_not_file_order(self):
        part1 = C2PA_MARK + b"AAA"
        part2 = b"BBB"
        lbox_tbox = part1[:8]
        segs = _mock_make_jpeg(
            _mock_make_app11(1, 2, lbox_tbox + part2),
            _mock_make_app11(1, 1, part1),
        )

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(segs)

        assert result == part1 + part2

    def test_many_fragments_assembled(self):
        chunks = [C2PA_MARK] + [bytes([i] * 100) for i in range(10)]
        lbox_tbox = chunks[0][:8]

        def make_fragment(z: int, chunk: bytes) -> bytes:
            payload = chunk if z == 1 else lbox_tbox + chunk
            return _mock_make_app11(1, z, payload)

        segs = _mock_make_jpeg(*[make_fragment(z + 1, chunk) for z, chunk in enumerate(chunks)])

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(segs)

        assert result == b"".join(chunks)


class TestExtractManifestStoreFromJpegRanges:
    def test_no_c2pa_returns_none_and_empty_ranges(self):
        result, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(
                _mock_make_app11(1, 1, b"not_c2pa"),
            ),
        )

        assert (result, ranges) == (None, [])

    def test_empty_bytes_returns_none_and_empty_ranges(self):
        result, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(b"")

        assert (result, ranges) == (None, [])

    def test_single_segment_range_matches_segment_bounds(self):
        seg = _mock_make_app11(1, 1, STORE)
        jpeg = _mock_make_jpeg(seg)
        result, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg)

        assert result == STORE

        # SOI (2 bytes) then the segment.
        assert ranges == [
            (2, 2 + len(seg)),
        ]

        # Splicing out the range leaves only SOI + EOI.
        start, end = ranges[0]
        assert jpeg[:start] + jpeg[end:] == b"\xff\xd8\xff\xd9"

    def test_multi_segment_ranges_cover_all_fragments(self):
        seg1_data = C2PA_MARK + b"part_one"
        lbox_tbox = seg1_data[:8]
        
        seg1 = _mock_make_app11(1, 1, seg1_data)
        seg2 = _mock_make_app11(1, 2, lbox_tbox + b"part_two")

        jpeg = _mock_make_jpeg(seg1, seg2)

        result, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg)

        assert result == C2PA_MARK + b"part_one" + b"part_two"
        assert ranges == [
            (2, 2 + len(seg1)),
            (2 + len(seg1), 2 + len(seg1) + len(seg2)),
        ]

    def test_ranges_only_cover_c2pa_segments_when_mixed(self):
        c2pa_seg = _mock_make_app11(1, 1, STORE)
        other_seg = _mock_make_app11(2, 1, b"other non-c2pa jumbf")
        jpeg = _mock_make_jpeg(c2pa_seg, other_seg)
        _, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg)

        assert ranges == [
            (2, 2 + len(c2pa_seg)),
        ]

    def test_ranges_returned_sorted_by_position(self):
        seg_a = _mock_make_app11(1, 1, C2PA_MARK + b"first_store")
        seg_b = _mock_make_app11(2, 1, C2PA_MARK + b"second_store")
        jpeg = _mock_make_jpeg(seg_a, seg_b)
        _, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg)

        assert ranges == sorted(ranges)
        assert ranges == [
            (2, 2 + len(seg_a)),
            (2 + len(seg_a), 2 + len(seg_a) + len(seg_b)),
        ]


class TestMultipleJpegStores:
    def test_returns_last_store_by_file_position(self):
        first = _mock_make_app11(1, 1, C2PA_MARK + b"first_store")
        second = _mock_make_app11(2, 1, C2PA_MARK + b"second_store")
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(_mock_make_jpeg(first, second))

        assert result == C2PA_MARK + b"second_store"

    def test_non_c2pa_store_does_not_replace_c2pa(self):
        c2pa_seg = _mock_make_app11(1, 1, STORE)
        other_seg = _mock_make_app11(2, 1, b"other non-c2pa jumbf")

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(_mock_make_jpeg(c2pa_seg, other_seg))

        assert result == STORE

    def test_raw_jpeg_with_two_stores_contains_two_ffeb(self):
        first = _mock_make_app11(1, 1, C2PA_MARK + b"first_store")
        second = _mock_make_app11(2, 1, C2PA_MARK + b"second_store")

        assert _mock_make_jpeg(first, second).count(b"\xff\xeb") >= 2


class TestJpegEdgeCases:
    def test_ffeb_lookalike_does_not_crash(self):
        garbage = b"\xff\xeb\x00\x05junk"
        real_seg = _mock_make_app11(1, 1, STORE)
        jpeg = b"\xff\xd8" + garbage + real_seg + b"\xff\xd9"

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg)

        assert result == STORE

    def test_truncated_segment_does_not_crash(self):
        seg = _mock_make_app11(1, 1, STORE)[:-5]
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(b"\xff\xd8" + seg + b"\xff\xd9")

        assert result is None or isinstance(result, bytes)

    def test_ffeb_inside_payload_not_double_counted(self):
        data = STORE + b"\xff\xeb\x00\x05extra"

        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(
            _mock_make_jpeg(
                _mock_make_app11(1, 1, data),
            ),
        )

        assert result == data


class TestJpegRealFile:
    def test_extracts_something(
        self,
        signed_jpg_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(signed_jpg_bytes)

        assert result is not None
        assert len(result) > 0

    def test_extracted_is_valid_jumbf(
        self,
        signed_jpg_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(signed_jpg_bytes)
        first_box, _ = Box.parse_from_bytes(result, 0)

        assert first_box.get_type() == JUMB_TYPE

    def test_extracted_is_manifest_store(
        self,
        signed_jpg_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(signed_jpg_bytes)
        first_box, _ = Box.parse_from_bytes(result, 0)
        children = list(iter_boxes(first_box.get_payload()))

        assert len(children) > 0
        assert children[0].get_type() == JUMD_TYPE

    def test_result_size_matches_jumbf_lbox(
        self,
        signed_jpg_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_jpeg(signed_jpg_bytes)
        lbox = int.from_bytes(result[:4], "big")

        if lbox == 1:
            xlbox = int.from_bytes(result[8:16], "big")

            assert len(result) >= xlbox
        else:
            assert len(result) >= lbox


class TestPdfManifestExtractor:
    def test_extracts_something(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)

        assert result is not None
        assert len(result) > 0

    def test_extracted_is_valid_jumbf(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)

        first_box, _ = Box.parse_from_bytes(result, 0)
        assert first_box.get_type() == JUMB_TYPE

    def test_extracted_is_manifest_store(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)

        first_box, _ = Box.parse_from_bytes(result, 0)
        children = list(iter_boxes(first_box.get_payload()))

        assert len(children) > 0
        assert children[0].get_type() == JUMD_TYPE


class TestActiveManifestWithRealFile:
    def test_get_active_manifest_uuid_matches_expected(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)
        uuid = get_active_manifest_uuid(result)

        assert uuid == EXPECTED_ACTIVE_UUID

    def test_find_manifest_by_expected_uuid(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)

        manifest_box = find_box_by_label(result, EXPECTED_ACTIVE_UUID)

        assert manifest_box is not None
        assert manifest_box.get_type() == JUMB_TYPE

    def test_active_is_last_manifest(
        self,
        signed_pdf_bytes: bytes,
    ):
        result, _ = extract_manifest_store_bytes_and_ranges_from_pdf(signed_pdf_bytes)
        store_box = SuperBox.from_box(Box.parse_from_bytes(result, 0)[0])

        manifest_labels = []
        for child in store_box.content_boxes:
            if child.get_type() != JUMB_TYPE:
                continue
            inner = list(iter_boxes(child.get_payload()))
            if not inner or inner[0].get_type() != JUMD_TYPE:
                continue

            label = jumd_label(inner[0].get_payload())
            if label:
                manifest_labels.append(label)

        assert len(manifest_labels) > 0
        assert manifest_labels[-1] == EXPECTED_ACTIVE_UUID


class TestMultiplePdfStores:
    def test_raw_pdf_contains_two_store_signatures(
        self,
        signed_pdf_bytes: bytes,
    ):
        count = signed_pdf_bytes.count(b"/application#2Fc2pa")

        assert count >= 2
