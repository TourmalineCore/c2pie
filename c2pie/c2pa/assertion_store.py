from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.content_types import c2pa_content_types


class AssertionStore(SuperBox):
    def __init__(
        self,
        assertions: list[Assertion],
    ):
        self.assertions = assertions

        super().__init__(
            content_type=c2pa_content_types["assertions"],
            label="c2pa.assertions",
            content_boxes=self.assertions,
        )

    def get_assertions(self) -> list:
        return self.assertions

    def add_full_c2pa_structure_exclusion(
        self,
        offset: int,
        length: int,
    ) -> None:
        for assertion in self.assertions:
            if assertion.type == C2PA_AssertionTypes.data_hash:
                assertion.add_full_c2pa_structure_exclusion(
                    offset,
                    length,
                )

        self.sync_payload()
