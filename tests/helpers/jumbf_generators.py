import struct


def _mock_make_box(
    box_type: bytes,
    payload: bytes = b"",
) -> bytes:
    l_box = 8 + len(payload)
    return l_box.to_bytes(4, "big") + box_type + payload


def _mock_make_jumd_payload(label: str) -> bytes:
    return b"\x00" * 16 + b"\x00" + label.encode("utf-8") + b"\x00"


def _mock_make_superbox(label: str, *children: bytes) -> bytes:
    jumd_box = _mock_make_box(b"jumd", _mock_make_jumd_payload(label))
    return _mock_make_box(b"jumb", jumd_box + b"".join(children))


def _mock_make_app11(
    en: int,
    z: int,
    fragment: bytes,
) -> bytes:
    payload = b"JP" + struct.pack(">HI", en, z) + fragment

    # The segment length includes two bytes of length
    seg_len = len(payload) + 2

    return b"\xff\xeb" + struct.pack(">H", seg_len) + payload


def _mock_make_jpeg(*app11_segments: bytes) -> bytes:
    # 0xFFD8 - SOI, 0xFFD9 - EOF
    return b"\xff\xd8" + b"".join(app11_segments) + b"\xff\xd9"
