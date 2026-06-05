import re
from collections import defaultdict
from collections.abc import Callable

from c2pie.utils.content_types import C2PA_ContentTypes


def extract_manifest_store_bytes_and_ranges_from_jpeg(
    jpeg_bytes: bytes,
) -> tuple[bytes | None, list[tuple[int, int]]]:
    """
    Scans the APP11 segments of a JPEG in a single pass and returns:

    - the raw JUMBF Manifest Store bytes of the active (last by file position)
      Manifest Store, or None if there is none.
    - the (start, end) byte ranges of every APP11 segment that belongs to a
      C2PA manifest store, so callers can splice them out of the file.

    A dictionary containing the sequence number (Z) and bytes of the APP11
    segment chunk, grouped by the APP11 segment identifier (EN).

    streams = {
        0: (             ; first APP11 segment identifier (EN)
            0: b'...',   ; first APP11 chunk identifier (Z)
            1: b'...',   ; second APP11 chunk identifier (Z)
            ...
        )
    }

    For more info see: docs/JPG-structure-overview.md
    """
    streams: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    first_offsets: dict[int, int] = {}
    segment_ranges: dict[int, list[tuple[int, int]]] = defaultdict(list)

    i = 0
    while (i := jpeg_bytes.find(b"\xff\xeb", i)) != -1:
        if i + 4 > len(jpeg_bytes):
            break

        seg_len = int.from_bytes(jpeg_bytes[i + 2 : i + 4], "big")
        seg_end = i + 2 + seg_len
        payload = jpeg_bytes[i + 4 : seg_end]

        if len(payload) >= 8 and payload[:2] == b"JP":
            en = int.from_bytes(payload[2:4], "big")
            z = int.from_bytes(payload[4:8], "big")

            if en not in first_offsets:
                first_offsets[en] = i

            # Z = 1: payload[8:] includes LBox+TBox as the start of the JUMBF box.
            # Z > 1: payload[8:16] is the repeated LBox+TBox prefix.
            # We should skip it to get the continuation bytes only.
            chunk = payload[8:] if z == 1 else payload[16:]
            streams[en].append((z, chunk))
            segment_ranges[en].append((i, seg_end))

        i = seg_end

    if not streams:
        return None, []

    candidates: list[tuple[int, bytes]] = []
    c2pa_ranges: list[tuple[int, int]] = []

    for en, parts in streams.items():
        parts.sort(key=lambda x: x[0])
        box = b"".join(fragment for _, fragment in parts)

        if b"urn:c2pa:" in box:
            candidates.append((first_offsets[en], box))
            c2pa_ranges.extend(segment_ranges[en])

    if not candidates:
        return None, []

    candidates.sort(key=lambda x: x[0])
    c2pa_ranges.sort()

    return candidates[-1][1], c2pa_ranges


def extract_manifest_store_bytes_and_ranges_from_pdf(
    pdf_bytes: bytes,
) -> tuple[bytes | None, list[tuple[int, int]]]:
    """
    Returns the raw JUMBF ManifestStore bytes from the last
    C2PA EmbeddedFile stream, plus an empty range list.
    """
    matches = list(
        re.finditer(
            rb"/Type /EmbeddedFile /Subtype /application#2Fc2pa /Length (\d+).*?stream[\r\n]+",
            pdf_bytes,
            re.DOTALL,
        )
    )

    if not matches:
        return None, []

    last_match = matches[-1]
    length = int(last_match.group(1))
    start = last_match.end()

    # The range list is always empty because in PDF, the Manifest Store
    # is added via incremental updates. An empty list is returned
    # for symmetry with other extractors.
    return pdf_bytes[start : start + length], []


_EXTRACTORS: dict[
    C2PA_ContentTypes,
    Callable[[bytes], tuple[bytes | None, list[tuple[int, int]]]],
] = {
    C2PA_ContentTypes.jpg: extract_manifest_store_bytes_and_ranges_from_jpeg,
    C2PA_ContentTypes.jpeg: extract_manifest_store_bytes_and_ranges_from_jpeg,
    C2PA_ContentTypes.pdf: extract_manifest_store_bytes_and_ranges_from_pdf,
}


def extract_manifest_store_bytes(
    content_type: C2PA_ContentTypes,
    raw_data: bytes,
) -> tuple[bytes | None, list[tuple[int, int]]]:
    extractor = _EXTRACTORS[content_type]
    return extractor(raw_data)
