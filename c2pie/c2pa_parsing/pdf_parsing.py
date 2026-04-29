from __future__ import annotations

import re


def extract_manifest_store_bytes_from_pdf(pdf_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the LAST C2PA EmbeddedFile stream."""
    # Find ALL matches, take the last one — that's the active store
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
