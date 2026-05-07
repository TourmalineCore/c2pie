# Jumbf super box class
from __future__ import annotations

from c2pie.jumbf_boxes.box import Box, iter_boxes
from c2pie.jumbf_boxes.constants import JUMB_TYPE
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.description_box import DescriptionBox
from c2pie.utils.content_types import jumbf_content_types


class SuperBox(Box):
    def __init__(
        self,
        content_type: bytes = jumbf_content_types["json"],
        label: str = "",
        content_boxes: list | None = None,
    ):
        self.description_box = DescriptionBox(content_type=content_type, label=label)
        self.content_boxes = [] if content_boxes is None else content_boxes

        payload = self.description_box.serialize() + self.serialize_content_boxes()
        super().__init__(b"jumb".hex(), payload=payload)

    @classmethod
    def from_box(
        cls,
        box: Box,
    ) -> SuperBox:
        if box.get_type() != JUMB_TYPE:
            raise ValueError("Box is not a JUMBF superbox")

        children = list(iter_boxes(box.get_payload()))
        if not children:
            raise ValueError("Empty JUMBF superbox")

        description_box = DescriptionBox.from_box(children[0])
        content_boxes = children[1:]

        instance = cls.__new__(cls)
        instance.t_box = box.get_type()
        instance.l_box = box.get_length()
        instance.payload = box.get_payload()
        instance.description_box = description_box
        instance.content_boxes = content_boxes
        return instance

    def _serialize_children(self) -> bytes:
        return b"".join(cb.serialize() for cb in self.content_boxes if cb is not None)

    def add_content_box(
        self,
        content_box: ContentBox,
    ):
        self.content_boxes.append(content_box)
        self.sync_payload()

    def serialize_content_boxes(self) -> bytes:
        serialized_content_boxes = b""

        for content_box in self.content_boxes:
            if content_box is not None:
                serialized_content_boxes += content_box.serialize()

        return serialized_content_boxes

    def sync_payload(self):
        self.payload = self.description_box.serialize() + self.serialize_content_boxes()
        super().__init__(b"jumb".hex(), payload=self.payload)

    def get_label(self) -> str:
        return self.description_box.get_label()

    def get_content_type(self) -> bytes:
        return self.description_box.get_content_type()
