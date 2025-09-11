# Content jumbf box class

from c2pie.jumbf_boxes.box import Box


class ContentBox(Box):
    def __init__(
        self,
        box_type: str = b"json".hex(),
        payload: bytes = b"",
    ):  # noqa: B008
        super().__init__(box_type=box_type, payload=payload)
