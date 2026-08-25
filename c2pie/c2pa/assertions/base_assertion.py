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


class Assertion(SuperBox):
    """Universal assertion superbox (one content box)."""

    def __init__(
        self,
        assertion_type: C2PA_AssertionTypes,
        content_boxes: list[ContentBox],
    ):
        self.type = assertion_type

        super().__init__(
            content_type=get_assertion_content_type(self.type),
            label=get_assertion_label(self.type),
            content_boxes=content_boxes,
        )

    def get_data_for_signing(self) -> bytes:
        return self.description_box.serialize() + self.serialize_content_boxes()

    @staticmethod
    def get_payload_from_schema(assertion_type: C2PA_AssertionTypes, schema: dict[str, Any]) -> bytes:
        content_type = get_assertion_content_type(assertion_type)

        if content_type == jumbf_content_types["json"]:
            return json_to_bytes(schema)
        elif content_type == jumbf_content_types["cbor"]:
            return cbor_to_bytes(schema)

        raise ValueError(f"Content type of {assertion_type.name!r} is not convertable from schema")

    @staticmethod
    def content_box_from_schema(assertion_type: C2PA_AssertionTypes, schema: dict[str, Any]) -> list[ContentBox]:
        payload = Assertion.get_payload_from_schema(assertion_type, schema)

        box_type_hex = get_assertion_content_box_type(assertion_type)
        return [
            ContentBox(
                box_type=box_type_hex,
                payload=payload,
            )
        ]
