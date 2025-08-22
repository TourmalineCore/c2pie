from __future__ import annotations

from typing import Any

from tc_c2pa_py.jumbf_boxes.content_box import ContentBox
from tc_c2pa_py.jumbf_boxes.super_box import SuperBox
from tc_c2pa_py.utils.assertion_schemas import (
    C2PA_AssertionTypes,
    cbor_to_bytes,
    get_assertion_content_box_type,
    get_assertion_content_type,
    get_assertion_label,
    json_to_bytes,
)
from tc_c2pa_py.utils.content_types import jumbf_content_types


class Assertion(SuperBox):
    """Universal assertion superbox (one content box)."""

    def __init__(self, assertion_type: C2PA_AssertionTypes, schema: dict[str, Any]):
        self.type = assertion_type
        self.schema = schema

        payload = self.get_payload_from_schema()
        box_type_hex = get_assertion_content_box_type(self.type)
        content_box = ContentBox(box_type=box_type_hex, payload=payload)

        super().__init__(
            content_type=get_assertion_content_type(self.type),
            label=get_assertion_label(self.type),
            content_boxes=[content_box],
        )

    def get_payload_from_schema(self) -> bytes:
        ctype = get_assertion_content_type(self.type)
        if ctype == jumbf_content_types["json"]:
            return json_to_bytes(self.schema)
        if ctype == jumbf_content_types["cbor"]:
            return cbor_to_bytes(self.schema)
        if ctype == jumbf_content_types["codestream"]:
            return self.schema.get("payload", b"")
        return b""

    def get_data_for_signing(self) -> bytes:
        return self.description_box.serialize() + self.serialize_content_boxes()


class HashDataAssertion(Assertion):
    """c2pa.hash.data hard binding assertion."""

    def __init__(
        self,
        cai_offset: int,
        hashed_data: bytes,
        additional_exclusions: list[dict[str, int]] | None = None,
    ):
        exclusions: list[dict[str, int]] = [{"start": cai_offset, "length": 65535}]
        if additional_exclusions:
            exclusions.extend(additional_exclusions)

        schema: dict[str, Any] = {
            "name": "jumbf manifest",
            "exclusions": exclusions,
            "alg": "sha256",
            "hash": hashed_data,
            "pad": [],
        }
        super().__init__(C2PA_AssertionTypes.data_hash, schema)

    def set_hash_data_length(self, length: int) -> None:
        if self.schema.get("name") != "jumbf manifest":
            return
        ex = self.schema.get("exclusions", [])
        if not ex:
            raise ValueError("c2pa.hash.data: exclusions are missing")
        ex[0]["length"] = int(length)

        payload = self.get_payload_from_schema()
        if self.content_boxes:
            self.content_boxes[0] = ContentBox(
                box_type=get_assertion_content_box_type(self.type),
                payload=payload,
            )
        else:
            self.content_boxes = [
                ContentBox(
                    box_type=get_assertion_content_box_type(self.type),
                    payload=payload,
                )
            ]
        self.sync_payload()
