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
    # We need to jump over the bytes containing the type (4 byte) and length (4 byte)
    # of the JUMBF box to reach the payload.
    while offset + 8 <= len(data):
        l_box = int.from_bytes(data[offset : offset + 4], "big")
        t_box = data[offset + 4 : offset + 8]

        # A JUMBF Box cannot be less than 8 bytes (t_box + l_box = 8 bytes).
        # offset + l_box > len(data) may be when JUMBF Box is corrupted.
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

    # The Description Box cannot be less than 17 bytes, since the UUID
    # is 16 bytes (fixed) and the label is at least 1 byte.
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

    # `boxes[0].payload`` is the Manifest Store payload, i.e., all the manifests.
    # The `manifest_store_boxes` list contains Manifest Store Description Box + all Content Boxes (Manifests).
    manifest_store_boxes = parse_boxes(boxes[0].payload)

    # Returns a list of raw Manifests bytes.
    return [manifest.raw_bytes for manifest in manifest_store_boxes[1:] if manifest.t_box == b"jumb"]


def find_active_manifest(manifest_store_bytes: bytes) -> ActiveManifestInfo:
    """Returns label and raw JUMBF bytes of the last (active) manifest in the store."""

    # Extracting JUMBF Boxes from C2PA structure.
    boxes = parse_boxes(manifest_store_bytes)

    if not boxes:
        raise ValueError("No JUMBF boxes found")

    # Extracting Minifest Store JUMBF Box.
    store_box = boxes[0]
    if store_box.t_box != b"jumb":
        raise ValueError("Root box is not a SuperBox")

    # Extracting the Description Box and Content Boxes from the Manifest Store payload.
    manifest_store_boxes = parse_boxes(store_box.payload)
    if not manifest_store_boxes or manifest_store_boxes[0].t_box != b"jumd":
        raise ValueError("ManifestStore has no DescriptionBox")

    # Extract the UUID from the Description Box and verify that it matches the required value.
    uuid, _ = parse_description_box_payload(manifest_store_boxes[0].payload)
    if uuid != c2pa_content_types["manifest_store"]:
        raise ValueError("Root box is not a ManifestStore")

    # Extracting Manifests from Content Boxes in the Manifest Store.
    manifest_boxes = [manifest for manifest in manifest_store_boxes[1:] if manifest.t_box == b"jumb"]
    if not manifest_boxes:
        raise ValueError("No manifests found in ManifestStore")

    active = manifest_boxes[-1]
    active_children = parse_boxes(active.payload)
    if not active_children or active_children[0].t_box != b"jumd":
        raise ValueError("Active manifest has no DescriptionBox")

    # Extracting the Manifest label (URN) so we can use its value later.
    _, label = parse_description_box_payload(active_children[0].payload)
    return ActiveManifestInfo(label=label, raw_bytes=active.raw_bytes)
