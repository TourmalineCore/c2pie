from __future__ import annotations

from pathlib import Path

import pytest

from c2pie.c2pa_parsing.jumbf_parsing import extract_manifest_boxes, jumd_label
from c2pie.c2pa_parsing.manifest_extractor import extract_manifest_store_bytes_from_pdf
from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import JUMB_TYPE, LABEL_OFFSET


def make_box(
    box_type: bytes,
    payload: bytes = b"",
) -> bytes:
    l_box = 8 + len(payload)
    return l_box.to_bytes(4, "big") + box_type + payload


def _mock_make_jumd_payload(label: str) -> bytes:
    return b"\x00" * 16 + b"\x00" + label.encode("utf-8") + b"\x00"


def _mock_make_superbox(label: str, *children: bytes) -> bytes:
    jumd_box = make_box(b"jumd", _mock_make_jumd_payload(label))
    return make_box(b"jumb", jumd_box + b"".join(children))


def _mock_get_label(box: Box) -> str | None:
    description_box = next(iter_boxes(box.get_payload()), None)
    return jumd_label(description_box.get_payload()) if description_box else None


@pytest.fixture
def signed_pdf_bytes() -> bytes:
    path = Path(__file__).parent.parent / "test_files" / "signed_signed_test_doc.pdf"
    return path.read_bytes()


class TestExtractManifestBoxes:
    def test_returns_empty_list_for_empty_bytes(self):
        assert extract_manifest_boxes(b"") == []

    def test_returns_empty_list_for_invalid_bytes(self):
        assert extract_manifest_boxes(b"\xff\xff\xff\xff") == []

    def test_returns_empty_list_if_root_is_not_jumb(self):
        bytes = make_box(
            b"jumd",
            b"",
        )
        assert extract_manifest_boxes(bytes) == []

    def test_skips_non_jumb_children(self):
        json_box = make_box(
            b"json",
            b"",
        )
        assert extract_manifest_boxes(json_box) == []

    def test_skips_jumb_child_with_non_jumd_first_box(self):
        json_box = make_box(
            b"json",
            b"data",
        )
        superbox = make_box(b"jumb", json_box)
        assert extract_manifest_boxes(superbox) == []

    def test_skips_manifest_with_non_c2pa_label(self):
        superbox = _mock_make_superbox("urn:uuid:some-uuid")
        assert extract_manifest_boxes(superbox) == []

    def test_skips_manifest_with_too_short_jumd_payload(self):
        short_payload = b"\x00" * (LABEL_OFFSET - 1)
        description_box = make_box(
            b"jumd",
            short_payload,
        )
        superbox = make_box(
            b"jumb",
            description_box,
        )
        assert extract_manifest_boxes(superbox) == []

    def test_skips_manifest_with_label_missing_null_terminator(self):
        payload = b"\x00" * 16 + b"\x00" + b"urn:c2pa:some-uuid"
        description_box = make_box(
            b"jumd",
            payload,
        )
        superbox = make_box(
            b"jumb",
            description_box,
        )
        assert extract_manifest_boxes(superbox) == []

    def test_returns_single_manifest(self):
        manifest_store = _mock_make_superbox(
            "manifest-store-label",
            _mock_make_superbox("urn:c2pa:some-uuid"),
        )
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert len(manifest_boxes) == 1

    def test_returns_multiple_c2pa_manifests(self):
        manifest_store = _mock_make_superbox(
            "manifest-store-label",
            _mock_make_superbox("urn:c2pa:some-uuid"),
            _mock_make_superbox("urn:c2pa:some-uuid"),
        )
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert len(manifest_boxes) == 2

    def test_returned_box_has_jumb_type(self):
        manifest_store = _mock_make_superbox(
            "manifest-store-label",
            _mock_make_superbox("urn:c2pa:some-uuid"),
        )
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert manifest_boxes[0].get_type() == JUMB_TYPE

    def test_filters_mixed_manifests(self):
        manifest_store = _mock_make_superbox(
            "manifest-store-label",
            _mock_make_superbox("urn:c2pa:some-uuid"),
            _mock_make_superbox("urn:c2pa:some-uuid"),
            make_box(b"json", b"urn:c2pa:some-uuid"),
        )
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert len(manifest_boxes) == 2
        assert manifest_boxes[0].get_type() == JUMB_TYPE

    def test_preserves_order_of_c2pa_manifests(self):
        manifest_store = _mock_make_superbox(
            "manifest-store-label",
            _mock_make_superbox("urn:c2pa:first"),
            _mock_make_superbox("urn:uuid:old"),
            _mock_make_superbox("urn:c2pa:second"),
            _mock_make_superbox("urn:c2pa:third"),
        )
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert [_mock_get_label(b) for b in manifest_boxes] == [
            "urn:c2pa:first",
            "urn:c2pa:second",
            "urn:c2pa:third",
        ]

    def test_returns_list_for_real_pdf(
        self,
        signed_pdf_bytes: bytes,
    ):
        manifest_store = extract_manifest_store_bytes_from_pdf(signed_pdf_bytes)
        manifest_boxes = extract_manifest_boxes(manifest_store)
        assert isinstance(manifest_boxes, list)
        for box in manifest_boxes:
            assert box.get_type() == JUMB_TYPE
