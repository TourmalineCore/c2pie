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
        previous_exclusions = list(self.schema["exclusions"])
        pad_length = len(self.schema["pad"])

        self.schema["exclusions"].extend(
            [
                {
                    "start": offset,
                    "length": length,
                },
            ]
        )
        current_exclusions = self.schema["exclusions"]

        updated_pad_length = self._calculate_updated_pad_length(
            previous_pad_length=pad_length,
            previous_exclusions=previous_exclusions,
            current_exclusions=current_exclusions,
        )

        self.schema["pad"] = b"\x00" * updated_pad_length

        payload = self.get_payload_from_schema(C2PA_AssertionTypes.data_hash, self.schema)

        self.content_boxes = [
            ContentBox(
                box_type=get_assertion_content_box_type(self.type),
                payload=payload,
            )
        ]

        self.sync_payload()

    def _calculate_updated_pad_length(
        self,
        previous_pad_length: int,
        previous_exclusions: list[dict[str, int]],
        current_exclusions: list[dict[str, int]],
    ) -> int:
        # NOTE: If the number of exclusions exceeds 24, an additional length byte
        # will be added to the CBOR header of serialized exclusions array. This byte
        # is included in the recalculation of the serialized exclusions.
        previous_exclusions_length: int = len(cbor_to_bytes(previous_exclusions))
        current_exclusions_length: int = len(cbor_to_bytes(current_exclusions))

        pad_difference: int = current_exclusions_length - previous_exclusions_length

        # If exclusions grew by more bytes than the pad has reserved, there is
        # no way to compensate without changing the total assertion size, which
        # would break the hard binding hash calculation.
        if pad_difference > previous_pad_length:
            raise ValueError("Exclusion exceed the reserved pad in Hash Assertion.")

        updated_pad_length: int = previous_pad_length - pad_difference

        # CBOR encodes a byte-string length header as 1 byte when the length is
        # 0-23, and as 2+ bytes when the length is 24 or more. If the pad drops
        # from >= 24 bytes to < 24 bytes, its own header shrinks by 1 byte.
        # Add 1 byte back to the pad to compensate for that shrinkage and keep
        # the total schema size unchanged.
        if updated_pad_length < 24 <= previous_pad_length:
            updated_pad_length += 1

        # If the pad has been fully consumed and would go negative, there is
        # no valid pad length left to represent — fail loudly instead of
        # silently producing an empty/invalid pad (e.g. b"\x00" * -1 == b"").
        if updated_pad_length < 0:
            raise ValueError("Not enough reserved pad to accommodate exclusion; increase initial pad size.")

        return updated_pad_length
