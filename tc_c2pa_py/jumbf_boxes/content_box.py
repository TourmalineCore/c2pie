# Content jumbf box class

from tc_c2pa_py.jumbf_boxes.box import Box


class ContentBox(Box):
    def __init__(self, box_type=b"json".hex(), payload=b""):  # noqa: B008
        super().__init__(box_type=box_type, payload=payload)
