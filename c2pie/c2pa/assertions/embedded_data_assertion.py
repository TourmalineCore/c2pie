from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes


class EmbeddedDataAssertion(Assertion):
    """
    Embedded Data assertion, contains embedded data within the JUMBF Box.

    Can be used for the following assertions:
    - c2pa.thumbnail.claim,
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
