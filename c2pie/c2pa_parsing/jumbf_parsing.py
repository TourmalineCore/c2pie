from __future__ import annotations

from c2pie.c2pa.manifest import Manifest
from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import (
    JUMB_TYPE,
    JUMD_TYPE,
    LABEL_OFFSET,
)


def jumd_label(payload: bytes) -> str | None:
    """
    Extracts the UTF-8 label from a JUMD (description box) payload.

    The label starts at LABEL_OFFSET and is null-terminated.
    Returns None if the payload is too short or the null terminator is missing.
    """
    if len(payload) < LABEL_OFFSET + 1:
        return None

    raw_label = payload[LABEL_OFFSET:]
    null_terminator = raw_label.find(b"\x00")

    if null_terminator == -1:
        return None

    return raw_label[:null_terminator].decode("utf-8")


def find_box_by_label(
    data: bytes,
    wanted_label: str,
) -> Box | None:
    """
    Searches the JUMBF box tree for the first superbox whose JUMD label
    matches `wanted_label`.

    Performs a depth-first traversal of all top-level boxes in `data`.
    Returns the matching superbox or None if not found.
    """
    for box in iter_boxes(data):
        found = _find_in_box(box, wanted_label)
        if found is not None:
            return found
    return None


def _find_in_box(
    box: Box,
    wanted_label: str,
) -> Box | None:
    """
    Recursively searches inside a single superbox for a JUMD label match.

    Skips non-JUMB boxes and boxes without a leading JUMD child.
    Returns the matching superbox or None.
    """
    if box.get_type() != JUMB_TYPE:
        return None

    children = list(iter_boxes(box.get_payload()))
    if not children or children[0].get_type() != JUMD_TYPE:
        return None

    if jumd_label(children[0].get_payload()) == wanted_label:
        return box

    for child in children[1:]:
        found = _find_in_box(child, wanted_label)
        if found is not None:
            return found

    return None


def extract_manifest_boxes(manifest_store_bytes: bytes) -> list[Manifest]:
    """Returns raw JUMBF bytes of each manifest (urn:c2pa:…) box in the store."""
    try:
        manifest_store_box, _ = Box.parse_from_bytes(manifest_store_bytes, 0)
    except ValueError:
        return []

    if manifest_store_box.get_type() != JUMB_TYPE:
        return []

    manifests: list[Manifest] = []
    for manifest in iter_boxes(manifest_store_box.get_payload()):
        if manifest.get_type() != JUMB_TYPE:
            continue

        manifest_boxes = list(iter_boxes(manifest.get_payload()))
        if not manifest_boxes or manifest_boxes[0].get_type() != JUMD_TYPE:
            continue

        label = jumd_label(manifest_boxes[0].get_payload())

        if label and label.startswith("urn:c2pa:"):
            manifest_class = Manifest(manifest_label=label)
            manifest_class.set_claim_signature(manifest_boxes[1])
            manifest_class.set_claim(manifest_boxes[2])
            manifest_class.set_assertion_store(manifest_boxes[3])

            manifests.append(manifest_class)

    return manifests


def get_active_manifest_uuid(manifest_store_bytes: bytes) -> str | None:
    """
    Returns the URN label of the active manifest from a raw JUMBF Manifest Store.

    The active manifest is defined as the last manifest box (JUMB with a JUMD label)
    within the Manifest Store superbox, as per the C2PA specification.
    Returns None if the data is not a valid JUMBF box or contains no manifests.
    """
    try:
        manifest_store_box, _ = Box.parse_from_bytes(manifest_store_bytes, 0)
    except ValueError:
        return None

    if manifest_store_box.get_type() != JUMB_TYPE:
        return None

    active_manifest_urn: str | None = None

    for child in iter_boxes(manifest_store_box.get_payload()):
        if child.get_type() != JUMB_TYPE:
            continue

        manifest = list(iter_boxes(child.get_payload()))
        if not manifest or manifest[0].get_type() != JUMD_TYPE:
            continue

        label = jumd_label(manifest[0].get_payload())
        if label:
            active_manifest_urn = label

    return active_manifest_urn
