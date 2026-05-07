import enum
import json
from typing import Any

import cbor2

from c2pie.utils.content_types import jumbf_content_types


class C2PA_AssertionTypes(enum.Enum):
    data_hash = 0
    embedded_data = 1
    thumbnail = 2
    actions = 3
    ingredient = 4


def json_to_bytes(json_object: dict[str, Any]) -> bytes:
    return json.dumps(json_object, separators=(",", ":")).encode("utf-8")


def cbor_to_bytes(json_object: dict[str, Any]) -> bytes:
    return cbor2.dumps(json_object)


def get_assertion_content_type(assertion_type: C2PA_AssertionTypes) -> bytes:
    if assertion_type == C2PA_AssertionTypes.data_hash:
        return jumbf_content_types["cbor"]
    elif assertion_type == C2PA_AssertionTypes.actions:
        return jumbf_content_types["cbor"]
    elif assertion_type == C2PA_AssertionTypes.embedded_data:
        return jumbf_content_types["embedded_file"]
    elif assertion_type == C2PA_AssertionTypes.thumbnail:
        return jumbf_content_types["embedded_file"]
    elif assertion_type == C2PA_AssertionTypes.ingredient:
        return jumbf_content_types["cbor"]
    else:
        return b""


def get_assertion_content_box_type(assertion_type: C2PA_AssertionTypes) -> str:
    if assertion_type == C2PA_AssertionTypes.data_hash:
        return b"cbor".hex()
    elif assertion_type == C2PA_AssertionTypes.actions:
        return b"cbor".hex()
    elif assertion_type == C2PA_AssertionTypes.ingredient:
        return b"cbor".hex()
    else:
        return b"".hex()


def get_assertion_label(assertion_type: C2PA_AssertionTypes) -> str:
    if assertion_type == C2PA_AssertionTypes.data_hash:
        return "c2pa.hash.data"
    elif assertion_type == C2PA_AssertionTypes.actions:
        return "c2pa.actions.v2"
    elif assertion_type == C2PA_AssertionTypes.embedded_data:
        return "c2pa.embedded-data"
    elif assertion_type == C2PA_AssertionTypes.thumbnail:
        return "c2pa.thumbnail.claim"
    elif assertion_type == C2PA_AssertionTypes.ingredient:
        return "c2pa.ingredient.v2"
    else:
        return ""
