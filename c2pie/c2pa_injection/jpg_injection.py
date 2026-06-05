from c2pie.c2pa.manifest_store import ManifestStore

# JPG_SEGMENT_MAX_PAYLOAD_LENGTH =
#   65535 (max segment length)
#   - 2 (bytes of length)
#   - 2 (bytes of CI)
#   - 2 (bytes of EN)
#   - 4 (bytes of Z)
JPG_SEGMENT_MAX_PAYLOAD_LENGTH = 65525


class JpgSegment:
    def __init__(
        self,
        payload_length: int,
        marker: bytes = bytes.fromhex("EB"),
    ):  # noqa: B008
        self.marker = marker
        self.payload_length = payload_length

    def get_segment_length(self):
        return self.payload_length + 2  # payload length + size of marker bytes length

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
    def __init__(
        self,
        segment_id,
        sequence_number,
        payload_length,
        payload,
    ):
        self.ci = bytes.fromhex(b"JP".hex())  # 2 bytes
        self.en = segment_id.to_bytes(2, "big")  # 2 bytes
        self.z = sequence_number.to_bytes(4, "big")  # 4 bytes

        self.app11_payload = payload

        super().__init__(
            payload_length=self.get_payload_length(payload_length),
        )

    def get_payload_length(
        self,
        payload_length,
    ):
        return 2 + 2 + 4 + payload_length

    def serialize(
        self,
        payload=None,
    ):
        app11_payload = self.ci + self.en + self.z + self.app11_payload

        return super().serialize(app11_payload)


class JpgSegmentApp11Storage:
    def __init__(
        self,
        payload: bytes,
    ):
        self.payload = payload
        self.serialized_length = 0

    def get_serialized_length(self):
        return self.serialized_length

    def serialize(self):
        # CI: JPEG extensions marker - JP.
        # EN: Box instance number.
        # Z: Packet sequence number.

        # TODO: It must not conflict with any other identifiers, if they exist.
        # We choose it randomly, but we will need to handle this case in the future.
        segment_id = 411
        sequence_number = 0
        payload_offset = 0

        remaining = len(self.payload)

        # Every segment after Z=1 must repeat the LBox + TBox (first 8 bytes of the JUMBF box)
        # immediately after CI + EN + Z. This frees 8 bytes from the max chunk size for those segments.
        lbox_tbox = self.payload[0:8]

        app11_segments = []

        while remaining > 0:
            sequence_number += 1  # The Z starts with 1.

            if sequence_number == 1:
                max_chunk = JPG_SEGMENT_MAX_PAYLOAD_LENGTH
                chunk = self.payload[payload_offset : payload_offset + max_chunk]
                segment_payload = chunk
            else:
                # Leave 8 bytes for the mandatory LBox + TBox prefix.
                max_chunk = JPG_SEGMENT_MAX_PAYLOAD_LENGTH - 8
                chunk = self.payload[payload_offset : payload_offset + max_chunk]
                segment_payload = lbox_tbox + chunk

            chunk_length = len(chunk)

            app11_segments.append(
                JpgSegmentApp11(
                    segment_id=segment_id,
                    sequence_number=sequence_number,
                    payload_length=len(segment_payload),
                    payload=segment_payload,
                )
            )

            remaining -= chunk_length
            payload_offset += chunk_length

        serialized_storage_data = b""
        for app11_segment in app11_segments:
            serialized_storage_data += app11_segment.serialize()

        self.serialized_length = len(serialized_storage_data)
        return serialized_storage_data


def create_and_serialize_app11_storage(
    manifest_store: ManifestStore,
) -> bytes:
    serialized_manifest_store = manifest_store.serialize()

    app11_storage = JpgSegmentApp11Storage(
        payload=serialized_manifest_store,
    )

    return app11_storage.serialize()


def emplace_manifest_into_jpeg(
    content_bytes: bytes,
    manifest_store: ManifestStore,
    c2pa_offset: int,
) -> bytes:
    serialized_app11_storage = create_and_serialize_app11_storage(manifest_store)

    serialized_app11_storage_length = len(serialized_app11_storage)

    manifest_store.add_full_c2pa_structure_exclusion(
        c2pa_offset,
        serialized_app11_storage_length,
    )

    tail = create_and_serialize_app11_storage(manifest_store)

    return content_bytes[:c2pa_offset] + tail + content_bytes[c2pa_offset:]
