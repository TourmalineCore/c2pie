from __future__ import annotations

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
        schema: dict[str, Any],
        content_boxes: list[ContentBox] | None = None,
    ):
        self.type = assertion_type
        self.schema = schema

        if content_boxes is None:
            payload = self.get_payload_from_schema()
            box_type_hex = get_assertion_content_box_type(self.type)
            content_boxes = [ContentBox(box_type=box_type_hex, payload=payload)]

        super().__init__(
            content_type=get_assertion_content_type(self.type),
            label=get_assertion_label(self.type),
            content_boxes=content_boxes,
        )

    def get_payload_from_schema(self) -> bytes:
        ctype = get_assertion_content_type(self.type)

        if ctype == jumbf_content_types["json"]:
            return json_to_bytes(self.schema)
        elif ctype == jumbf_content_types["cbor"]:
            return cbor_to_bytes(self.schema)

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
            raise ValueError("c2pa.hash.data: jumbf manifest is missing")
        exclusions = self.schema.get("exclusions", [])
        if not exclusions:
            raise ValueError("c2pa.hash.data: exclusions are missing")
        exclusions[0]["length"] = int(length)

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


class ActionsAssertion(Assertion):
    """c2pa.actions.v2 assertion of actions on an asset."""

    def __init__(
        self,
        action: str,
        parameters: dict[str, list[dict[str, str]]] | None = None,
    ):
        schema: dict[str, Any] = {"actions": [{"action": action}]}

        if parameters is not None:
            schema["actions"][0]["parameters"] = parameters

        super().__init__(C2PA_AssertionTypes.actions, schema)


class EmbeddedDataAssertion(Assertion):
    """
    Embedded Data assertion, contains embedded data within the JUMBF Box.

    Can be used for the following assertions:
    - c2pa.thumbnail.claim,
    - c2pa.ingredient,
    - c2pa.ingredient.thumbnail
    - c2pa.embedded-data

    Structure:
    JUMBF Super Box (jumb)
    -> JUMBF Description Box (jumd)
    -> Embedded File Description Box (bfdb)
    -> Binary Data Box (bidb)
    """

    def __init__(
        self,
        media_type: str,
        image_data: bytes,
        assertion_type: C2PA_AssertionTypes = C2PA_AssertionTypes.embedded_data,
    ):
        # 0000 000x - Filename present? (0 - false, 1 - true)
        # 0000 00x0 - What's inside bidb? (0 - binary data, 1 - URI)
        # xxxx xx00- reserved
        toggles_bytes = b"\x00"

        # IANA media type + null-terminate
        media_type_bytes = media_type.encode("utf-8") + b"\x00"

        payload = toggles_bytes + media_type_bytes

        super().__init__(
            assertion_type=assertion_type,
            schema={},
            content_boxes=[
                ContentBox(
                    box_type=b"bfdb".hex(),  # UUID Type of Embedded File Description Box
                    payload=payload,
                ),
                ContentBox(
                    box_type=b"bidb".hex(),  # UUID Type of Binary Data Box
                    payload=image_data,
                ),
            ],
        )
