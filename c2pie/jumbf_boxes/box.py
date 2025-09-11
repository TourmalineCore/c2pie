# Base jumbf box class


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
