from __future__ import annotations

import re

_HEADER_PATTERN = re.compile(
    rb"<< /Type /EmbeddedFile /Subtype /application#2Fc2pa /Length (\d+) >>\nstream\n"
)


def extract_manifest_store_bytes(pdf_bytes: bytes) -> bytes | None:
    """Returns raw JUMBF ManifestStore bytes from the last C2PA EmbeddedFile stream, or None."""

    matches = list(_HEADER_PATTERN.finditer(pdf_bytes))

    if not matches:
        return None
    
    # We retrieve the Manifest Store from the last section, as it contains the current Manifest Store.
    last = matches[-1]
    # Retrieves the value of the first group (\d+) from _HEADER_PATTERN and converts it to a number.
    length = int(last.group(1))
    # Saves the byte position after a match of _HEADER_PATTERN.
    stream_start = last.end()

    return pdf_bytes[stream_start : stream_start + length]
