from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable

from c2pie.utils.content_types import C2PA_ContentTypes

_APP11_MARKER = 0xEB
_CI_MAGIC = b"JP"

# 0xD8 - SOI
# 0xD9 - EOI
# 0x01 - TEM marker
# set(range(0xD0, 0xD8) - restart markers, using in decode
# This dictionary contains all markers that are not followed by a length byte.
_STANDALONE_MARKERS = {0xD8, 0xD9, 0x01} | set(range(0xD0, 0xD8))


def extract_manifest_store_bytes_from_jpeg(jpeg_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the APP11 segment."""

    """
    A dictionary containing the sequence number (Z) and bytes of the APP11 
    segment chunk, grouped by the APP11 segment identifier (EN).

    app11_chunks = {
        0: (             ; first APP11 segment identifier (EN)
            0: b'...',   ; first APP11 chunk identifier (Z)
            1: b'...',   ; second APP11 chunk identifier (Z)
            ...
        )
    }

    For more info see: docs/JPG-structure-overview.md
    """
    app11_chunks: dict[int, list[tuple[int, bytes]]] = defaultdict(list)

    i = 2  # Jump forward 2 bytes to skip the SOI marker (0xFF, 0xD8)
    while i + 3 < len(jpeg_bytes):
        if jpeg_bytes[i] != 0xFF:
            next_ff = jpeg_bytes.find(b"\xff", i + 1)

            if next_ff == -1:
                break

            i = next_ff
            continue

        marker = jpeg_bytes[i + 1]

        # Exit when the raw image data marker is encountered. There may be cases where the SOS (0xDA)
        # marker is missing (corrupted image), so we also track the EOI (0xD9) marker
        if marker == 0xD9 or marker == 0xDA:
            break

        # If a marker without a length is encountered, jump over it
        if marker in _STANDALONE_MARKERS:
            i += 2
            continue

        # Checking for the existence of bytes of a length after the marker
        if i + 4 > len(jpeg_bytes):
            break

        # The segment length does not include marker bytes
        seg_len = int.from_bytes(jpeg_bytes[i + 2 : i + 4], "big")

        if marker == _APP11_MARKER:
            chunk_payload = jpeg_bytes[i + 4 : i + 2 + seg_len]

            if len(chunk_payload) >= 8 and chunk_payload[:2] == _CI_MAGIC:
                en = int.from_bytes(chunk_payload[2:4], "big")
                z = int.from_bytes(chunk_payload[4:8], "big")

                app11_chunks[en].append((z, chunk_payload[8:]))

        i += 2 + seg_len

    if not app11_chunks:
        return None

    app11_chunks = dict(sorted(app11_chunks.items()))

    manifest_stores: list[bytes] = []
    for _, chunks in app11_chunks.items():
        chunks.sort(key=lambda x: x[0])
        manifest_store = b"".join(chunk_bytes for _, chunk_bytes in chunks)

        if b"urn:c2pa:" in manifest_store:
            manifest_stores.append(manifest_store)

    if not manifest_stores:
        return None

    return manifest_stores[-1]


def extract_manifest_store_bytes_from_pdf(pdf_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the LAST C2PA EmbeddedFile stream."""

    # (\d+)  - captures the stream length in bytes (e.g. "4096")
    # .*?    - skips any additional PDF keys between /Length and stream (non-greedy)
    # stream - literal keyword marking the start of the binary data
    # [\r\n]+ - matches line ending after stream (LF, CRLF, or CR)
    matches = list(
        re.finditer(
            rb"/Type /EmbeddedFile /Subtype /application#2Fc2pa /Length (\d+).*?stream[\r\n]+",
            pdf_bytes,
            re.DOTALL,
        )
    )

    if not matches:
        return None

    # We retrieve the Manifest Store from the last section, as it contains the current Manifest Store
    last = matches[-1]
    # Retrieves the value of the first group (\d+) and converts it to a number
    length = int(last.group(1))
    # Saves the byte position after a match
    start = last.end()

    return pdf_bytes[start : start + length]


_EXTRACTORS: dict[C2PA_ContentTypes, Callable[[bytes], bytes | None]] = {
    C2PA_ContentTypes.jpg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.jpeg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.pdf: extract_manifest_store_bytes_from_pdf,
}


def extract_manifest_store_bytes(
    content_type: C2PA_ContentTypes,
    raw_data: bytes,
) -> bytes | None:
    extractor = _EXTRACTORS[content_type]
    return extractor(raw_data)
