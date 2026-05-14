from __future__ import annotations

import hashlib
import io
from typing import Any

import c2pa

from c2pie.c2pa_parsing.jumbf_parsing import _find_in_box
from c2pie.jumbf_boxes.box import Box
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

    def set_hash_data_length(
        self,
        length: int,
    ) -> None:
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
        parameters: dict[str, list[dict[str, Any]]] | None = None,
    ):
        if action not in _ALLOWED_ACTIONS:
            raise ValueError(f"Invalid action {action!r}. Must be one of: {_ALLOWED_ACTIONS}")

        schema: dict[str, Any] = {
            "actions": [
                {"action": action},
            ],
        }

        if parameters:
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


class ThumbnailAssertion(EmbeddedDataAssertion):
    """An assertion (c2pa.thumbnail.claim) containing an asset thumbnail"""

    def __init__(
        self,
        media_type: str,
        image_data: bytes,
    ):
        super().__init__(
            media_type=media_type,
            image_data=image_data,
            assertion_type=C2PA_AssertionTypes.thumbnail,
        )


def validate_ingredient(
    ingredient_bytes: bytes,
    mime_type: str,
) -> dict | None:
    stream = io.BytesIO(ingredient_bytes)
    reader = c2pa.Reader.try_create(mime_type, stream)

    if reader is None:
        return None

    with reader:
        return reader.get_validation_results()


def _generate_hashed_uri_map(
    url: str,
    hash_value: bytes,
    hash_algorithm: str | None = None,
) -> dict[str, str | bytes]:
    schema: dict[str, str | bytes] = {
        "url": url,
        "hash": hash_value,
    }

    if hash_algorithm:
        schema["alg"] = hash_algorithm

    return schema


class IngredientAssertion(Assertion):
    """c2pa.ingredient.v3 asset-binding assertion."""

    def __init__(
        self,
        title: str,
        dc_format: str,
        ingredient_bytes: bytes,
        active_manifest_urn: str | None,
        previous_manifest_boxes: list[Box],
    ):
        schema: dict[str, Any] = {
            "dc:title": title,
            "dc:format": dc_format,
            "relationship": "parentOf",
        }

        if active_manifest_urn and previous_manifest_boxes:
            validation_results = validate_ingredient(
                ingredient_bytes,
                dc_format,
            )

            # We should not include information about the active manifest if validation was unsuccessful
            if validation_results is None:
                super().__init__(
                    C2PA_AssertionTypes.ingredient,
                    schema,
                )

            active_manifest_box: Box = None
            for box in previous_manifest_boxes:
                found_box = _find_in_box(
                    box,
                    active_manifest_urn,
                )

                if found_box:
                    active_manifest_box = found_box
                    break

            # We should not include information about the active manifest if validation was unsuccessful
            if active_manifest_box:
                super().__init__(
                    C2PA_AssertionTypes.ingredient,
                    schema,
                )

            active_manifest_hash = hashlib.sha256(active_manifest_box.payload).digest()

            active_manifest: dict[str, str | bytes] = _generate_hashed_uri_map(
                url=f"self#jumbf=/c2pa/{active_manifest_urn}",
                hash_value=active_manifest_hash,
                hash_algorithm="sha256",
            )

            schema["activeManifest"] = active_manifest
            schema["validationResults"] = validation_results

        super().__init__(
            C2PA_AssertionTypes.ingredient,
            schema,
        )
