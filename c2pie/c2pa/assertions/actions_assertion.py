from typing import Any

from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes

_ALLOWED_ACTIONS = ["c2pa.created", "c2pa.opened"]


class ActionsAssertion(Assertion):
    """c2pa.actions.v2 assertion of actions on an asset."""

    def __init__(
        self,
        action: str,
        parameters: dict[str, list[dict[str, Any]]] | None = None,
    ):
        if action not in _ALLOWED_ACTIONS:
            raise ValueError(f"Invalid action {action!r}. Must be one of: {_ALLOWED_ACTIONS}")

        self.schema: dict[str, Any] = {
            "actions": [
                {"action": action},
            ],
        }

        if parameters:
            self.schema["actions"][0]["parameters"] = parameters

        content_boxes = self.content_box_from_schema(C2PA_AssertionTypes.actions, self.schema)

        super().__init__(C2PA_AssertionTypes.actions, content_boxes)
