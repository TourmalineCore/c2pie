from __future__ import annotations

from collections import defaultdict


def extract_manifest_store_bytes_from_jpeg(jpeg_bytes: bytes) -> bytes | None:
    streams: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    first_offset: dict[int, int] = {}

    i = 0
    while (i := jpeg_bytes.find(b"\xFF\xEB", i)) != -1:
        if i + 4 > len(jpeg_bytes):
            break

        seg_len = int.from_bytes(jpeg_bytes[i + 2 : i + 4], "big")
        payload  = jpeg_bytes[i + 4 : i + 2 + seg_len]

        if len(payload) >= 8 and payload[:2] == b"JP":
            en = int.from_bytes(payload[2:4], "big")
            z  = int.from_bytes(payload[4:8], "big")
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