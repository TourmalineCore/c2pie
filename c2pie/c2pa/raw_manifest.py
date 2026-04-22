from __future__ import annotations

from c2pie.c2pa_parsing.jumbf_reader import parse_boxes, parse_description_box_payload


class RawManifest:
    """Opaque wrapper for a serialized C2PA Manifest JUMBF box.

    Preserves raw bytes verbatim so existing manifest hashes remain valid.
    Full deserialization back into Manifest objects is reserved for future use —
    see to_manifest().
    """

    def __init__(self, raw_bytes: bytes):
        self._raw_bytes = raw_bytes
        self.label = self._extract_label()

    def serialize(self) -> bytes:
        return self._raw_bytes

    def set_hash_data_length(self, length: int) -> None:
        pass

    def to_manifest(self) -> "Manifest":  # noqa: F821
        raise NotImplementedError

    def _extract_label(self) -> str:
        try:
            children = parse_boxes(self._raw_bytes[8:])
            if children and children[0].t_box == b"jumd":
                _, label = parse_description_box_payload(children[0].payload)
                return label
        except Exception:
            pass
        return ""
