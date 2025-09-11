JPEG_SEGMENT_MAX_PAYLOAD_LENGTH = 65517


class JpgSegment:
    def __init__(
        self,
        payload_length: int,
        marker: bytes = bytes.fromhex("EB"),
    ):  # noqa: B008
        self.marker = marker
        self.payload_length = payload_length

    def get_segment_length(self):
        return self.payload_length + 2  # payload length + size of payload length

    def serialize(
        self,
        payload: bytes,
    ):
        serialized_data = b""

        serialized_data += bytes.fromhex("FF") + self.marker
        serialized_data += self.get_segment_length().to_bytes(2, "big")
        serialized_data += payload

        return serialized_data


class JpgSegmentApp11(JpgSegment):
    def __init__(self, segment_id, sequence_number, payload_length, payload):
        self.ci = bytes.fromhex(b"JP".hex())  # 2 bytes
        self.en = segment_id  # 2 bytes
        self.z = sequence_number  # 4 bytes

        self.app11_payload = payload

        super().__init__(payload_length=self.get_payload_length(payload_length))

    def get_payload_length(self, payload_length):
        return 2 + 2 + 4 + 4 + 4 + payload_length

    def serialize(self, payload=None):
        _en = self.en.to_bytes(2, "big")
        _z = self.z.to_bytes(4, "big")

        app11_payload = self.ci + _en + _z + self.app11_payload

        return super().serialize(app11_payload)


class JpgSegmentApp11Storage:
    def __init__(
        self,
        app11_segment_box_length: int,
        app11_segment_box_type: bytes,
        payload: bytes,
    ):
        self.l_box = app11_segment_box_length
        self.t_box = app11_segment_box_type
        self.payload = payload
        self.serialized_length = 0

    def get_payload_length(self):
        return self.l_box - 4 - 4  # - t_box_length - l_box_length

    def get_serialized_length(self):
        return self.serialized_length

    def serialize(self):
        segment_id = 1
        sequence_number = 0
        payload_offset = 0

        payload_length = self.get_payload_length()

        app11_segments = []

        while payload_length > 0:
            sequence_number += 1
            chunk_length = JPEG_SEGMENT_MAX_PAYLOAD_LENGTH
            if payload_length < JPEG_SEGMENT_MAX_PAYLOAD_LENGTH:
                chunk_length = payload_length

            app11_segments.append(
                JpgSegmentApp11(
                    segment_id=segment_id,
                    sequence_number=sequence_number,
                    payload_length=chunk_length,
                    payload=self.payload[payload_offset:],
                )
            )
            payload_length -= chunk_length
            payload_offset += chunk_length

        serialized_storage_data = b""
        for app11_segment in app11_segments:
            serialized_storage_data += app11_segment.serialize()

        self.serialized_length = len(serialized_storage_data)
        return serialized_storage_data
