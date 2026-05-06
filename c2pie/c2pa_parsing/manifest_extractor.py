from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable

from c2pie.utils.content_types import C2PA_ContentTypes


def extract_manifest_store_bytes_from_jpeg(jpeg_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the APP11 segment."""
    streams: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    first_offset: dict[int, int] = {}

    i = 0
    while (i := jpeg_bytes.find(b"\xff\xeb", i)) != -1:
        if i + 4 > len(jpeg_bytes):
            break

        seg_len = int.from_bytes(jpeg_bytes[i + 2 : i + 4], "big")
        payload = jpeg_bytes[i + 4 : i + 2 + seg_len]

        if len(payload) >= 8 and payload[:2] == b"JP":
            en = int.from_bytes(payload[2:4], "big")
            z = int.from_bytes(payload[4:8], "big")
            if en not in first_offset:
                first_offset[en] = i
            streams[en].append((z, payload[8:]))

        i += 2 + seg_len

    if not streams:
        return None

    candidates: list[tuple[int, bytes]] = []
    for en, parts in streams.items():
        parts.sort(key=lambda x: x[0])
        box = b"".join(fragment for _, fragment in parts)
        if b"urn:c2pa:" in box:
            candidates.append((first_offset[en], box))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]


def extract_manifest_store_bytes_from_pdf(pdf_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the LAST C2PA EmbeddedFile stream."""
    matches = list(
        re.finditer(
            rb"/Type /EmbeddedFile /Subtype /application#2Fc2pa /Length (\d+).*?stream[\r\n]+",
            pdf_bytes,
            re.DOTALL,
        )
    )
    if not matches:
        return None

    last_match = matches[-1]
    length = int(last_match.group(1))
    start = last_match.end()
    return pdf_bytes[start : start + length]


_EXTRACTORS: dict[C2PA_ContentTypes, Callable[[bytes], bytes | None]] = {
    C2PA_ContentTypes.jpg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.jpeg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.pdf: extract_manifest_store_bytes_from_pdf,
}


def extract_manifest_store_bytes(content_type: C2PA_ContentTypes, raw_data: bytes) -> bytes | None:
    extractor = _EXTRACTORS[content_type]
    return extractor(raw_data)
