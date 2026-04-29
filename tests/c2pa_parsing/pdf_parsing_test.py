from pathlib import Path

import pytest

from c2pie.c2pa_parsing.jumbf_parsing import (
    find_box_by_label,
    get_active_manifest_uuid,
    jumd_label,
)
from c2pie.c2pa_parsing.pdf_parsing import extract_manifest_store_bytes_from_pdf
from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import JUMB_TYPE, JUMD_TYPE
from c2pie.jumbf_boxes.super_box import SuperBox

EXPECTED_ACTIVE_UUID = "urn:uuid:712065da7bda430f8e425d2772b0a0b7"


@pytest.fixture
def signed_pdf_bytes() -> bytes:
    path = Path(__file__).parent.parent / "test_files" / "signed_signed_test_doc.pdf"
    return path.read_bytes()


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


class TestMultipleStores:
    def test_raw_pdf_contains_two_store_signatures(self, signed_pdf_bytes):
        count = signed_pdf_bytes.count(b"/application#2Fc2pa")
        assert count >= 2
