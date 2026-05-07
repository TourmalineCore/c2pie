# Base jumbf box class

from c2pie.jumbf_boxes.constants import (
    BYTE_ORDER,
    HEADER_SIZE,
    LBOX_SIZE,
)


class Box:
    def __init__(
        self,
        box_type: str,
        payload: bytes = b"",
    ):
        self.payload = payload  # Box payload
        self.t_box = box_type
        self.l_box = (
            len(bytes.fromhex(self.t_box)) + 4 + len(self.payload)
        )  # Size of box_type (4 bytes) + self size (4 bytes)

    def get_length(self):
        return self.l_box

    def get_type(self):
        return self.t_box

    def get_payload(self):
        return self.payload

    def serialize(self):
        t_box = bytes.fromhex(self.t_box)
        l_box = self.l_box.to_bytes(4, "big")
        return l_box + t_box + self.payload

    @classmethod
    def parse_from_bytes(
        cls,
        data: bytes,
        offset: int = 0,
    ) -> tuple["Box", int]:
        if offset + HEADER_SIZE > len(data):
            raise ValueError("Not enough data for box header")

        l_box = int.from_bytes(
            data[offset : offset + LBOX_SIZE],
            BYTE_ORDER,
        )
        t_box = data[offset + LBOX_SIZE : offset + HEADER_SIZE].hex()

        if l_box == 0:
            end = len(data)
        else:
            end = offset + l_box

        if end > len(data):
            raise ValueError("Box length exceeds available data")

        payload = data[offset + HEADER_SIZE : end]
        box = cls(t_box, payload)
        box.l_box = l_box
        return box, end


def iter_boxes(data: bytes):
    offset = 0
    while offset < len(data):
        box, offset = Box.parse_from_bytes(data, offset)
        yield box
