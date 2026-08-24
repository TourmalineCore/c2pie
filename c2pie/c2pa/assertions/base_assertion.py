from typing import Any

from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.assertion_schemas import (
    C2PA_AssertionTypes,
    cbor_to_bytes,
    get_assertion_content_box_type,
    get_assertion_content_type,
    get_assertion_label,
    json_to_bytes,
)
from c2pie.utils.content_types import jumbf_content_types

_ALLOWED_ACTIONS = ["c2pa.created", "c2pa.opened"]


class Assertion(SuperBox):
    """Universal assertion superbox (one content box)."""

    def __init__(
        self,
        assertion_type: C2PA_AssertionTypes,
        schema: dict[str, Any],
        content_boxes: list[ContentBox] | None = None,
    ):
        self.type = assertion_type
        self.schema = schema

        if not content_boxes:
            payload = self.get_payload_from_schema()
            box_type_hex = get_assertion_content_box_type(self.type)
            content_boxes = [
                ContentBox(
                    box_type=box_type_hex,
                    payload=payload,
                )
            ]

        super().__init__(
            content_type=get_assertion_content_type(self.type),
            label=get_assertion_label(self.type),
            content_boxes=content_boxes,
        )

    def get_payload_from_schema(self) -> bytes:
        content_type = get_assertion_content_type(self.type)

        if content_type == jumbf_content_types["json"]:
            return json_to_bytes(self.schema)
        elif content_type == jumbf_content_types["cbor"]:
            return cbor_to_bytes(self.schema)

        return b""

    def get_data_for_signing(self) -> bytes:
        return self.description_box.serialize() + self.serialize_content_boxes()
