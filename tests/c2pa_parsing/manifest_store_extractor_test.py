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
    extract_manifest_store_bytes_from_jpeg,
    extract_manifest_store_bytes_from_pdf,
)
from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import JUMB_TYPE, JUMD_TYPE
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.signing import _get_content_type_by_filepath
from c2pie.utils.content_types import C2PA_ContentTypes

C2PA_MARK = b"urn:c2pa:"
JUMBF = b"jumbf_box_data"
STORE = C2PA_MARK + JUMBF

EXPECTED_ACTIVE_UUID = "urn:uuid:712065da7bda430f8e425d2772b0a0b7"


def make_app11(en: int, z: int, fragment: bytes) -> bytes:
    payload = b"JP" + struct.pack(">HI", en, z) + fragment
    seg_len = len(payload) + 2
    return b"\xff\xeb" + struct.pack(">H", seg_len) + payload


def make_jpeg(*app11_segments: bytes) -> bytes:
    return b"\xff\xd8" + b"".join(app11_segments) + b"\xff\xd9"


@pytest.fixture
def signed_jpg_bytes() -> bytes:
    path = Path(__file__).parent.parent / "fixtures" / "big_c2pa_test_image.jpg"
    return path.read_bytes()


@pytest.fixture
def signed_pdf_bytes() -> bytes:
    path = Path(__file__).parent.parent / "fixtures" / "signed_signed_test_doc.pdf"
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

        result = extract_manifest_store_bytes(_get_content_type_by_filepath(path), pdf_bytes)

        assert result == b"urn:c2pa:pdf!!\n"

    def test_extract_manifest_store_bytes_dispatches_jpeg(self, tmp_path: Path):
        jpeg_bytes = make_jpeg(make_app11(1, 1, STORE))
        path = tmp_path / "sample.jpg"
        path.write_bytes(jpeg_bytes)

        result = extract_manifest_store_bytes(_get_content_type_by_filepath(path), jpeg_bytes)

        assert result == STORE

    def test_unsupported_extension_raises(self):
        with pytest.raises(ValueError):
            _get_content_type_by_filepath(Path("file.png"))


class TestJpegManifestExtractor:
    def test_extracts_something(self):
        result = extract_manifest_store_bytes_from_jpeg(make_jpeg(make_app11(1, 1, STORE)))
        assert result is not None
        assert len(result) > 0

    def test_returns_none_without_c2pa(self):
        assert extract_manifest_store_bytes_from_jpeg(make_jpeg()) is None

    def test_returns_none_for_empty_bytes(self):
        assert extract_manifest_store_bytes_from_jpeg(b"") is None

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


class TestMultipleJpegStores:
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
        assert make_jpeg(first, second).count(b"\xff\xeb") >= 2


class TestJpegEdgeCases:
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


class TestJpegRealFile:
    def test_extracts_something(self, signed_jpg_bytes: bytes):
        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        assert result is not None
        assert len(result) > 0

    def test_extracted_is_valid_jumbf(self, signed_jpg_bytes: bytes):
        result = extract_manifest_store_bytes_from_jpeg(signed_jpg_bytes)
        first_box, _ = Box.parse_from_bytes(result, 0)
        assert first_box.get_type() == JUMB_TYPE

    def test_extracted_is_manifest_store(self, signed_jpg_bytes: bytes):
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


class TestPdfManifestExtractor:
    def test_extracts_something(self, signed_pdf_bytes):
        result = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)

        assert result is not None
        assert len(result) > 0

    def test_extracted_is_valid_jumbf(self, signed_pdf_bytes):
        result = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)

        first_box, _ = Box.parse_from_bytes(result, 0)
        assert first_box.get_type() == JUMB_TYPE

    def test_extracted_is_manifest_store(self, signed_pdf_bytes):
        result = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)

        first_box, _ = Box.parse_from_bytes(result, 0)
        children = list(iter_boxes(first_box.get_payload()))

        assert len(children) > 0
        assert children[0].get_type() == JUMD_TYPE


class TestActiveManifestWithRealFile:
    def test_get_active_manifest_uuid_matches_expected(self, signed_pdf_bytes):
        store = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)
        uuid = get_active_manifest_uuid(store)

        assert uuid == EXPECTED_ACTIVE_UUID

    def test_find_manifest_by_expected_uuid(self, signed_pdf_bytes):
        store = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)

        manifest_box = find_box_by_label(store, EXPECTED_ACTIVE_UUID)

        assert manifest_box is not None
        assert manifest_box.get_type() == JUMB_TYPE

    def test_active_is_last_manifest(self, signed_pdf_bytes):
        store = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)
        store_box = SuperBox.from_box(Box.parse_from_bytes(store, 0)[0])

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
    def test_raw_pdf_contains_two_store_signatures(self, signed_pdf_bytes):
        count = signed_pdf_bytes.count(b"/application#2Fc2pa")
        assert count >= 2
