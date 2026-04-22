import pytest

from c2pie.c2pa_parsing.jumbf_reader import (
    ActiveManifestInfo,
    find_active_manifest,
    get_all_manifest_raw_bytes,
    parse_boxes,
    parse_description_box_payload,
)
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


def _make_manifest_super(label: str) -> SuperBox:
    return SuperBox(
        content_type=c2pa_content_types["default_manifest"],
        label=label,
        content_boxes=[ContentBox(box_type=b"cbor".hex(), payload=b"payload")],
    )


def _make_store(labels: list[str]) -> bytes:
    manifests = [_make_manifest_super(lb) for lb in labels]
    store = SuperBox(
        content_type=c2pa_content_types["manifest_store"],
        label="c2pa",
        content_boxes=manifests,
    )
    return store.serialize()


def test_parse_boxes_single():
    box = ContentBox(box_type=b"cbor".hex(), payload=b"data")
    boxes = parse_boxes(box.serialize())
    assert len(boxes) == 1
    assert boxes[0].t_box == b"cbor"
    assert boxes[0].payload == b"data"


def test_parse_boxes_multiple():
    b1 = ContentBox(box_type=b"cbor".hex(), payload=b"one")
    b2 = ContentBox(box_type=b"json".hex(), payload=b"two")
    data = b1.serialize() + b2.serialize()
    boxes = parse_boxes(data)
    assert len(boxes) == 2
    assert boxes[0].t_box == b"cbor"
    assert boxes[1].t_box == b"json"


def test_parse_boxes_lbox_equals_raw_bytes():
    box = ContentBox(box_type=b"cbor".hex(), payload=b"hello")
    boxes = parse_boxes(box.serialize())
    assert boxes[0].raw_bytes == box.serialize()
    assert boxes[0].l_box == len(box.serialize())


def test_parse_boxes_empty_data():
    assert parse_boxes(b"") == []


def test_parse_boxes_truncated_data():
    assert parse_boxes(b"\x00\x00\x00") == []


def test_parse_description_box_payload_extracts_uuid_and_label():
    sb = SuperBox(content_type=c2pa_content_types["manifest_store"], label="c2pa")
    children = parse_boxes(sb.serialize()[8:])  # skip outer jumb header
    desc = children[0]
    uuid, label = parse_description_box_payload(desc.payload)
    assert uuid == c2pa_content_types["manifest_store"]
    assert label == "c2pa"


def test_parse_description_box_payload_too_short():
    with pytest.raises(ValueError, match="too short"):
        parse_description_box_payload(b"\x00" * 10)


def test_find_active_manifest_single():
    store_bytes = _make_store(["urn:uuid:aaa"])
    info = find_active_manifest(store_bytes)
    assert isinstance(info, ActiveManifestInfo)
    assert info.label == "urn:uuid:aaa"


def test_find_active_manifest_multiple_returns_last():
    store_bytes = _make_store(["urn:uuid:first", "urn:uuid:second", "urn:uuid:third"])
    info = find_active_manifest(store_bytes)
    assert info.label == "urn:uuid:third"


def test_find_active_manifest_raw_bytes_is_valid_jumbf():
    store_bytes = _make_store(["urn:uuid:test"])
    info = find_active_manifest(store_bytes)
    assert info.raw_bytes[4:8] == b"jumb"


def test_find_active_manifest_invalid_uuid_raises():
    # SuperBox with wrong UUID (not a manifest_store)
    sb = SuperBox(content_type=c2pa_content_types["claim"], label="c2pa")
    with pytest.raises(ValueError, match="ManifestStore"):
        find_active_manifest(sb.serialize())


def test_find_active_manifest_empty_data_raises():
    with pytest.raises(ValueError):
        find_active_manifest(b"")


def test_get_all_manifest_raw_bytes_count():
    store_bytes = _make_store(["urn:uuid:a", "urn:uuid:b"])
    raw_list = get_all_manifest_raw_bytes(store_bytes)
    assert len(raw_list) == 2


def test_get_all_manifest_raw_bytes_order():
    store_bytes = _make_store(["urn:uuid:first", "urn:uuid:second"])
    raw_list = get_all_manifest_raw_bytes(store_bytes)
    # Each entry should be a valid jumb box
    for rb in raw_list:
        assert rb[4:8] == b"jumb"


def test_get_all_manifest_raw_bytes_empty_store():
    sb = SuperBox(content_type=c2pa_content_types["manifest_store"], label="c2pa", content_boxes=[])
    assert get_all_manifest_raw_bytes(sb.serialize()) == []
