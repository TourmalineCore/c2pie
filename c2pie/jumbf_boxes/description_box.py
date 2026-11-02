# Description jumbf box class

from c2pie.jumbf_boxes.box import Box
from c2pie.jumbf_boxes.constants import (
    CONTENT_TYPE_SIZE,
    LABEL_OFFSET,
)
from c2pie.utils.content_types import jumbf_content_types


class DescriptionBox(Box):
    def __init__(
        self,
        content_type: bytes = jumbf_content_types["json"],
        label: str = "",
    ):
        self.label = label
        self.content_type = content_type
        self.toggle = 3

        payload = self.content_type + self.toggle.to_bytes(1, "big") + self.label.encode("utf-8") + b"\x00"

        super().__init__(b"jumd".hex(), payload=payload)

    @classmethod
    def from_box(
        cls,
        box: Box,
    ) -> "DescriptionBox":
        payload = box.get_payload()
        if len(payload) < LABEL_OFFSET + 1:
            raise ValueError("JUMD payload is too short")

        null_terminator = payload.find(b"\x00", LABEL_OFFSET)
        if null_terminator == -1:
            raise ValueError("JUMD label is not null-terminated")

        instance = cls.__new__(cls)
        instance.t_box = box.get_type()
        instance.l_box = box.get_length()
        instance.payload = payload

        instance.content_type = payload[:CONTENT_TYPE_SIZE]
        instance.toggle = payload[CONTENT_TYPE_SIZE]
        instance.label = payload[LABEL_OFFSET:null_terminator].decode("utf-8")
        return instance

    def get_label(self) -> str:
        return self.label

    def get_content_type(self) -> bytes:
        return self.content_type
