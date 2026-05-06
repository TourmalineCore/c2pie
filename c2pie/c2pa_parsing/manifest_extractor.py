from __future__ import annotations

import re
from collections import defaultdict
from typing import Callable

from c2pie.utils.content_types import C2PA_ContentTypes
_EXTRACTORS: dict[C2PA_ContentTypes, Callable[[bytes], bytes | None]] = {
    C2PA_ContentTypes.jpg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.jpeg: extract_manifest_store_bytes_from_jpeg,
    C2PA_ContentTypes.pdf: extract_manifest_store_bytes_from_pdf,
}


def extract_manifest_store_bytes(content_type: C2PA_ContentTypes, raw_data: bytes) -> bytes | None:
    extractor = _EXTRACTORS[content_type]
    return extractor(raw_data)
