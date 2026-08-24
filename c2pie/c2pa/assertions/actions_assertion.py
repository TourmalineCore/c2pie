from typing import Any

from c2pie.c2pa.assertions.base_assertion import _ALLOWED_ACTIONS, Assertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes


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
