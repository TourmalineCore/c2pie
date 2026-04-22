from __future__ import annotations

from dataclasses import dataclass

from c2pie.utils.content_types import c2pa_content_types


@dataclass
class RawBox:
    t_box: bytes
    l_box: int
    payload: bytes
    raw_bytes: bytes


@dataclass
class ActiveManifestInfo:
    label: str
    raw_bytes: bytes


def parse_boxes(data: bytes) -> list[RawBox]:
    boxes: list[RawBox] = []
    offset = 0
    while offset + 8 <= len(data):
        l_box = int.from_bytes(data[offset : offset + 4], "big")
        t_box = data[offset + 4 : offset + 8]
        if l_box < 8 or offset + l_box > len(data):
            break
        payload = data[offset + 8 : offset + l_box]
        boxes.append(
            RawBox(
                t_box=t_box,
                l_box=l_box,
                payload=payload,
                raw_bytes=data[offset : offset + l_box],
            )
        )
        offset += l_box
    return boxes


def parse_description_box_payload(payload: bytes) -> tuple[bytes, str]:
    """Returns (uuid, label) from a jumd box payload."""
    if len(payload) < 17:
        raise ValueError("DescriptionBox payload too short")
    uuid = payload[:16]
    label = payload[17:].rstrip(b"\x00").decode("utf-8")
    return uuid, label


def get_all_manifest_raw_bytes(manifest_store_bytes: bytes) -> list[bytes]:
    """Returns raw JUMBF bytes for every manifest in the store, in order."""
    boxes = parse_boxes(manifest_store_bytes)
    if not boxes or boxes[0].t_box != b"jumb":
        return []
    children = parse_boxes(boxes[0].payload)
    return [c.raw_bytes for c in children[1:] if c.t_box == b"jumb"]


def find_active_manifest(manifest_store_bytes: bytes) -> ActiveManifestInfo:
    """Returns label and raw JUMBF bytes of the last (active) manifest in the store."""
    boxes = parse_boxes(manifest_store_bytes)
    if not boxes:
        raise ValueError("No JUMBF boxes found")

    store_box = boxes[0]
    if store_box.t_box != b"jumb":
        raise ValueError("Root box is not a SuperBox")

    children = parse_boxes(store_box.payload)
    if not children or children[0].t_box != b"jumd":
        raise ValueError("ManifestStore has no DescriptionBox")

    uuid, _ = parse_description_box_payload(children[0].payload)
    if uuid != c2pa_content_types["manifest_store"]:
        raise ValueError("Root box is not a ManifestStore")

    manifest_boxes = [c for c in children[1:] if c.t_box == b"jumb"]
    if not manifest_boxes:
        raise ValueError("No manifests found in ManifestStore")

    active = manifest_boxes[-1]
    active_children = parse_boxes(active.payload)
    if not active_children or active_children[0].t_box != b"jumd":
        raise ValueError("Active manifest has no DescriptionBox")

    _, label = parse_description_box_payload(active_children[0].payload)
    return ActiveManifestInfo(label=label, raw_bytes=active.raw_bytes)
