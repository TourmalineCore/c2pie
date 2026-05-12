from __future__ import annotations

from c2pie.c2pa.manifest import Manifest
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.c2pa_parsing.jumbf_parsing import extract_manifest_boxes
from c2pie.jumbf_boxes.box import Box
from c2pie.jumbf_boxes.constants import JUMB_TYPE


def _make_store_bytes(*labels: str) -> bytes:
    manifests = [Manifest(manifest_label=label) for label in labels]
    return ManifestStore(manifests=manifests).serialize()


class TestExtractManifestBoxes:
    def test_returns_list(self):
        store_bytes = _make_store_bytes("urn:c2pa:abc")
        result = extract_manifest_boxes(store_bytes)
        assert isinstance(result, list)

    def test_single_manifest_returns_one_box(self):
        store_bytes = _make_store_bytes("urn:c2pa:abc")
        result = extract_manifest_boxes(store_bytes)
        assert len(result) == 1

    def test_two_manifests_returns_two_boxes(self):
        store_bytes = _make_store_bytes("urn:c2pa:aaa", "urn:c2pa:bbb")
        result = extract_manifest_boxes(store_bytes)
        assert len(result) == 2

    def test_each_result_is_bytes(self):
        store_bytes = _make_store_bytes("urn:c2pa:abc")
        for box_bytes in extract_manifest_boxes(store_bytes):
            assert isinstance(box_bytes, bytes)

    def test_each_result_is_valid_jumb_box(self):
        store_bytes = _make_store_bytes("urn:c2pa:abc")
        for box_bytes in extract_manifest_boxes(store_bytes):
            box, _ = Box.parse_from_bytes(box_bytes, 0)
            assert box.get_type() == JUMB_TYPE

    def test_empty_bytes_returns_empty_list(self):
        assert extract_manifest_boxes(b"") == []

    def test_invalid_bytes_returns_empty_list(self):
        assert extract_manifest_boxes(b"\x00\x01\x02\x03garbage") == []

    def test_non_manifest_store_returns_empty_list(self):
        # Raw JUMB box without "c2pa" label — not a manifest store
        manifest_box = Manifest(manifest_label="urn:c2pa:xyz")
        raw = manifest_box.serialize()
        assert extract_manifest_boxes(raw) == []

    def test_roundtrip_prior_manifest_bytes_equal_original(self):
        urn = "urn:c2pa:roundtrip"
        store_bytes = _make_store_bytes(urn)
        boxes = extract_manifest_boxes(store_bytes)
        assert len(boxes) == 1
        # Re-parse the extracted box and verify it serializes back identically
        box, _ = Box.parse_from_bytes(boxes[0], 0)
        assert box.serialize() == boxes[0]
