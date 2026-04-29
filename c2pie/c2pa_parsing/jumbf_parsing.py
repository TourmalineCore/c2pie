from __future__ import annotations

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
    zero = raw_label.find(b"\x00")
    if zero == -1:
        return None

    return raw_label[:zero].decode("utf-8")


def find_box_by_label(data: bytes, wanted_label: str) -> Box | None:
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


def _find_in_box(box: Box, wanted_label: str) -> Box | None:
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


def get_active_manifest_uuid(manifest_store_bytes: bytes) -> str | None:
    """
    Returns the URN label of the active manifest from a raw JUMBF Manifest Store.

    The active manifest is defined as the last manifest box (JUMB with a JUMD label)
    within the Manifest Store superbox, as per the C2PA specification.
    Returns None if the data is not a valid JUMBF box or contains no manifests.
    """
    try:
        store, _ = Box.parse_from_bytes(manifest_store_bytes, 0)
    except ValueError:
        return None

    if store.get_type() != JUMB_TYPE:
        return None

    active_urn: str | None = None

    for child in iter_boxes(store.get_payload()):
        if child.get_type() != JUMB_TYPE:
            continue

        inner = list(iter_boxes(child.get_payload()))
        if not inner or inner[0].get_type() != JUMD_TYPE:
            continue

        label = jumd_label(inner[0].get_payload())
        if label:
            active_urn = label

    return active_urn
