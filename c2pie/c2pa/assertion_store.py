from __future__ import annotations

from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


class AssertionStore(SuperBox):
    def __init__(
        self,
        assertions: list,
    ):
        self.assertions = assertions
        super().__init__(
            content_type=c2pa_content_types["assertions"],
            label="c2pa.assertions",
            content_boxes=self.assertions,
        )

    def get_assertions(self) -> list:
        return self.assertions

    def set_hash_data_length(
        self,
        length: int,
    ) -> None:
        for assertion in self.assertions:
            if assertion.type == C2PA_AssertionTypes.data_hash:
                assertion.set_hash_data_length(length)
        self.sync_payload()
