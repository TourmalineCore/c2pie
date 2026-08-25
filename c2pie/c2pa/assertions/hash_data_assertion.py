from typing import Any

from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes, cbor_to_bytes, get_assertion_content_box_type


class HashDataAssertion(Assertion):
    """c2pa.hash.data hard binding assertion."""

    def __init__(
        self,
        hashed_data: bytes,
    ):
        exclusions: list[dict[str, int]] = []

        self.schema: dict[str, Any] = {
            "exclusions": exclusions,
            "alg": "sha256",
            "hash": hashed_data,
            # The specification recommends setting the pad to at least 16 bytes. We use 64 bytes
            # to allow for some extra space before the 23-byte limit is exceeded, since otherwise
            # the CBOR header of the pad field would be reduced by 1 byte.
            "pad": b"\x00" * 64,
        }
        content_boxes = self.content_box_from_schema(C2PA_AssertionTypes.data_hash, self.schema)

        super().__init__(C2PA_AssertionTypes.data_hash, content_boxes)

    def add_full_c2pa_structure_exclusion(
        self,
        offset: int,
        length: int,
    ) -> None:
        exclusions = self.schema["exclusions"]
        previous_exclusion_length = len(cbor_to_bytes(exclusions))

        self.schema["exclusions"].extend(
            [
                {
                    "start": offset,
                    "length": length,
                },
            ]
        )

        # NOTE: If the number of exclusions exceeds 23, an additional length byte
        # will be added to the CBOR header of serialized exclusions array. This byte
        # is included in the recalculation of the serialized exclusions.
        current_exclusion_length = len(cbor_to_bytes(exclusions))

        difference = previous_exclusion_length - current_exclusion_length

        if -difference > len(self.schema["pad"]):
            raise ValueError("Difference in length exceeds the predefined pad")

        # If the pad is less than 24 bytes the size of the cbor header
        # will change during conversion to cbor and will occupy less than 2 bytes.
        updated_pad_length = len(self.schema["pad"]) + difference

        # If a CBOR overflow is not handled, the extra length byte that
        # would be added in this case will not be taken into account.
        if updated_pad_length < 24:
            updated_pad_length -= 1

        self.schema["pad"] = b"\x00" * updated_pad_length

        payload = self.get_payload_from_schema(C2PA_AssertionTypes.data_hash, self.schema)

        self.content_boxes = [
            ContentBox(
                box_type=get_assertion_content_box_type(self.type),
                payload=payload,
            )
        ]

        self.sync_payload()
