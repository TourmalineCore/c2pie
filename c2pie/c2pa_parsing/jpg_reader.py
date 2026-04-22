from __future__ import annotations

_APP11_MARKER = 0xEB
_CI_MAGIC = b"JP"
_STANDALONE_MARKERS = {0xD8, 0xD9, 0x01} | set(range(0xD0, 0xD8))


def _scan_app11_chunks(jpg_bytes: bytes) -> dict[int, dict[int, bytes]]:
    """Returns {segment_id: {sequence_number: chunk_bytes}}."""
    segments: dict[int, dict[int, bytes]] = {}
    i = 2  # skip SOI

    while i + 3 < len(jpg_bytes):
        if jpg_bytes[i] != 0xFF:
            break
        marker = jpg_bytes[i + 1]

        if marker == 0xD9 or marker == 0xDA:
            break

        if marker in _STANDALONE_MARKERS:
            i += 2
            continue

        if i + 4 > len(jpg_bytes):
            break

        seg_length = int.from_bytes(jpg_bytes[i + 2 : i + 4], "big")
        seg_end = i + 2 + seg_length

        if marker == _APP11_MARKER:
            content = jpg_bytes[i + 4 : seg_end]
            if len(content) >= 8 and content[:2] == _CI_MAGIC:
                en = int.from_bytes(content[2:4], "big")
                z = int.from_bytes(content[4:8], "big")
                chunk = content[8:]
                segments.setdefault(en, {})[z] = chunk

        i = seg_end

    return segments


def extract_manifest_store_bytes(jpg_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes assembled from APP11 segments, or None."""
    segments = _scan_app11_chunks(jpg_bytes)
    if not segments:
        return None

    seg_id = min(segments.keys())
    chunks = segments[seg_id]
    assembled = b"".join(chunks[z] for z in sorted(chunks.keys()))

    if len(assembled) < 8 or assembled[4:8] != b"jumb":
        return None

    return assembled


def extract_raw_image_bytes(jpg_bytes: bytes) -> bytes:
    """Returns JPG bytes with all C2PA APP11 segments (CI=JP) removed."""
    result = bytearray(jpg_bytes[:2])  # preserve SOI
    i = 2

    while i + 1 < len(jpg_bytes):
        if jpg_bytes[i] != 0xFF:
            result.extend(jpg_bytes[i:])
            break

        marker = jpg_bytes[i + 1]

        if marker == 0xD9 or marker == 0xDA:
            result.extend(jpg_bytes[i:])
            break

        if marker in _STANDALONE_MARKERS:
            result.extend(jpg_bytes[i : i + 2])
            i += 2
            continue

        if i + 4 > len(jpg_bytes):
            result.extend(jpg_bytes[i:])
            break

        seg_length = int.from_bytes(jpg_bytes[i + 2 : i + 4], "big")
        seg_end = i + 2 + seg_length

        if marker == _APP11_MARKER:
            content = jpg_bytes[i + 4 : seg_end]
            if len(content) >= 2 and content[:2] == _CI_MAGIC:
                i = seg_end
                continue

        result.extend(jpg_bytes[i:seg_end])
        i = seg_end

    return bytes(result)
