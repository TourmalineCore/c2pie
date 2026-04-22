import pytest

from c2pie.c2pa.raw_manifest import RawManifest
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


def _make_manifest_bytes(label: str = "urn:uuid:test") -> bytes:
    return SuperBox(
        content_type=c2pa_content_types["default_manifest"],
        label=label,
        content_boxes=[ContentBox(box_type=b"cbor".hex(), payload=b"data")],
    ).serialize()


def test_raw_manifest_serialize_roundtrip():
    raw = _make_manifest_bytes()
    rm = RawManifest(raw)
    assert rm.serialize() == raw


def test_raw_manifest_extracts_label():
    rm = RawManifest(_make_manifest_bytes("urn:uuid:hello"))
    assert rm.label == "urn:uuid:hello"


def test_raw_manifest_set_hash_data_length_is_noop():
    raw = _make_manifest_bytes()
    rm = RawManifest(raw)
    rm.set_hash_data_length(9999)
    assert rm.serialize() == raw


def test_raw_manifest_in_manifest_store():
    raw = _make_manifest_bytes("urn:uuid:existing")
    rm = RawManifest(raw)
    store = ManifestStore([rm])
    serialized = store.serialize()
    assert raw in serialized


def test_raw_manifest_in_manifest_store_serializes_without_error():
    rm = RawManifest(_make_manifest_bytes())
    store = ManifestStore([rm])
    assert len(store.serialize()) > 0


def test_to_manifest_raises_not_implemented():
    rm = RawManifest(_make_manifest_bytes())
    with pytest.raises(NotImplementedError):
        rm.to_manifest()


def test_raw_manifest_invalid_bytes_label_falls_back_to_empty():
    rm = RawManifest(b"\x00" * 20)
    assert rm.label == ""
