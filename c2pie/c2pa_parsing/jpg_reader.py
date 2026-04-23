from __future__ import annotations

_APP11_MARKER = 0xEB
_CI_MAGIC = b"JP"

# 0xD8 - SOI
# 0xD9 - EOI
# 0x01 - TEM marker
# set(range(0xD0, 0xD8) - restart markers, using in decode
# This dictionary contains all markers that are not followed by a length byte.
_STANDALONE_MARKERS = {0xD8, 0xD9, 0x01} | set(range(0xD0, 0xD8))


def _scan_app11_chunks(jpg_bytes: bytes) -> dict[int, dict[int, bytes]]:
    """Returns {segment_id: {sequence_number: chunk_bytes}}."""

    """
    {
        1: {
            0: b'...',
            1: b'...',
            ...
        }
    }
    """
    segments: dict[int, dict[int, bytes]] = {}
    i = 2  # We jump forward 2 bytes to skip the SOI marker (0xFF, 0xD8).

    # Jump through the segments until the APP11 (0xEB) marker is found.
    while i + 3 < len(jpg_bytes):
        if jpg_bytes[i] != 0xFF:
            break

        marker = jpg_bytes[i + 1]

        # Exit when the raw image data marker is encountered. There may be cases where the SOS (0xDA)
        # marker is missing (corrupted image), so we also track the EOI (0xD9) marker.
        if marker == 0xD9 or marker == 0xDA:
            break

        # If a marker without a length is encountered, jump over it.
        if marker in _STANDALONE_MARKERS:
            i += 2
            continue

        # Checking for the existence of bytes of a length after the marker.
        if i + 4 > len(jpg_bytes):
            break

        seg_length = int.from_bytes(jpg_bytes[i + 2 : i + 4], "big")
        seg_end = i + 2 + seg_length  # The segment length does not include marker bytes.

        if marker == _APP11_MARKER:
            content = jpg_bytes[i + 4 : seg_end]

            # See docs/JPG-structure-overview.md
            if len(content) >= 8 and content[:2] == _CI_MAGIC:
                en = int.from_bytes(content[2:4], "big")
                z = int.from_bytes(content[4:8], "big")
                chunk = content[8:]

                # The maximum segment length is 65535 (0xFFFF), so a Manifest Store can be split
                # and contained in multiple APP11 segments. The EN number identifies a specific Manifest Store,
                # and the Z number identifies the parts into which the Manifest Store has been split.
                segments.setdefault(en, {})[z] = chunk

        i = seg_end

    return segments


def extract_manifest_store_bytes(jpg_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes assembled from APP11 segments, or None."""

    segments = _scan_app11_chunks(jpg_bytes)

    if not segments:
        return None

    # NOTE: In C2PA, the `segments` dictionary cannot contain more than one entry (Manifest Store).

    # ID of Manifest Store (EN).
    seg_id = min(segments.keys())
    # A dictionary with chunks from the Manifest Store, where each entry has a sequence number (Z).
    chunks = segments[seg_id]
    # A single byte string containing bytes from all chunks.
    assembled_byte_string = b"".join(chunks[z] for z in sorted(chunks.keys()))

    if len(assembled_byte_string) < 8 or assembled_byte_string[4:8] != b"jumb":
        return None

    return assembled_byte_string


def extract_raw_image_bytes(jpg_bytes: bytes) -> bytes:
    """Returns JPG bytes with all C2PA APP11 segments (CI=JP) removed."""
    
    # We jump forward 2 bytes to skip the SOI marker (0xFF, 0xD8).
    result = bytearray(jpg_bytes[:2])
    i = 2

    while i + 1 < len(jpg_bytes):
        # This condition will be true when there is an entry in the raw image bytes.
        if jpg_bytes[i] != 0xFF:
            result.extend(jpg_bytes[i:])
            break

        marker = jpg_bytes[i + 1]

        # Add bytes and exit when the raw image data marker is encountered. There may be cases where 
        # the SOS (0xDA) marker is missing (corrupted image), so we also track the EOI (0xD9) marker.
        if marker == 0xD9 or marker == 0xDA:
            result.extend(jpg_bytes[i:])
            break
        
        # If a marker without a length is encountered, add it and jump over it.
        if marker in _STANDALONE_MARKERS:
            result.extend(jpg_bytes[i : i + 2])
            i += 2
            continue
        
        # Checking for the existence of bytes of a length after the marker.
        if i + 4 > len(jpg_bytes):
            result.extend(jpg_bytes[i:])
            break

        seg_length = int.from_bytes(jpg_bytes[i + 2 : i + 4], "big")
        seg_end = i + 2 + seg_length  # The segment length does not include marker bytes.

        if marker == _APP11_MARKER:
            content = jpg_bytes[i + 4 : seg_end]

            # We need to jump over the APP11 segment with the C2PA structure to exclude it from hashing.
            if len(content) >= 2 and content[:2] == _CI_MAGIC:
                i = seg_end
                continue

        result.extend(jpg_bytes[i:seg_end])
        i = seg_end

    return bytes(result)
