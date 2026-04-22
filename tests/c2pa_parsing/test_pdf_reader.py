from c2pie.c2pa_parsing.pdf_reader import extract_manifest_store_bytes


def _make_embedded_file_section(store_bytes: bytes, obj_num: int = 1) -> bytes:
    length = len(store_bytes)
    obj = (
        f"{obj_num} 0 obj\n<< /Type /EmbeddedFile /Subtype /application#2Fc2pa /Length {length} >>\nstream\n"
    ).encode("ascii")
    return obj + store_bytes + b"\nendstream\nendobj\n"


def _make_pdf_without_c2pa() -> bytes:
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
        b"xref\n0 2\n0000000000 65535 f \n0000000009 00000 n \n"
        b"trailer\n<< /Size 2 /Root 1 0 R >>\nstartxref\n9\n%%EOF\n"
    )


def _make_pdf_with_c2pa(store_bytes: bytes) -> bytes:
    section = _make_embedded_file_section(store_bytes, obj_num=2)
    return _make_pdf_without_c2pa() + section


def test_extract_store_bytes_returns_none_without_c2pa():
    pdf = _make_pdf_without_c2pa()
    assert extract_manifest_store_bytes(pdf) is None


def test_extract_store_bytes_returns_stream_content():
    store_bytes = b"\x00" * 16 + b"jumb" + b"\xab" * 20
    pdf = _make_pdf_with_c2pa(store_bytes)
    result = extract_manifest_store_bytes(pdf)
    assert result == store_bytes


def test_extract_store_bytes_returns_last_section():
    store_first = b"\x00" * 16 + b"jumb" + b"\xaa" * 10
    store_last = b"\x00" * 16 + b"jumb" + b"\xbb" * 10
    section1 = _make_embedded_file_section(store_first, obj_num=2)
    section2 = _make_embedded_file_section(store_last, obj_num=10)
    pdf = _make_pdf_without_c2pa() + section1 + section2
    result = extract_manifest_store_bytes(pdf)
    assert result == store_last


def test_extract_store_bytes_binary_content():
    store_bytes = bytes(range(256)) * 2
    pdf = _make_pdf_with_c2pa(store_bytes)
    result = extract_manifest_store_bytes(pdf)
    assert result == store_bytes


def test_extract_store_bytes_with_endstream_sequence_inside():
    # Regex-based extraction would truncate here; Length-based extraction must not.
    store_bytes = b"\xde\xad" + b"\nendstream" + b"\xbe\xef" * 8
    pdf = _make_pdf_with_c2pa(store_bytes)
    result = extract_manifest_store_bytes(pdf)
    assert result == store_bytes
