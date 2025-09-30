from __future__ import annotations

import re
from io import BytesIO
from typing import NamedTuple

from pypdf import PdfWriter

from c2pie.c2pa.config import RETRY_SIGNATURE
from c2pie.c2pa.manifest_store import ManifestStore


class PdfInfo(NamedTuple):
    content: bytes
    startxref: int
    max_obj: int
    pages_ref: str


def _read_pdf_using_pypdf(initial_content: bytes) -> bytes:
    input_stream = BytesIO(initial_content)
    output_stream = BytesIO()
    pdf_writer = PdfWriter(input_stream)
    pdf_writer.write(output_stream)
    output_stream.seek(0)
    byte_string = output_stream.read()
    return byte_string


def _find_startxref(bytes: bytes) -> int:
    patterns = list(re.finditer(rb"startxref\s+(\d+)\s*%%EOF\s*$", bytes, re.DOTALL))
    if not patterns:
        raise ValueError("startxref not found")
    return int(patterns[-1].group(1))


def _get_max_obj_num(bytes: bytes) -> int:
    object_numbers = [int(m.group(1)) for m in re.finditer(rb"\n(\d+)\s+0\s+obj\b", bytes)]
    return max(object_numbers) if object_numbers else 0


def _extract_pages_ref(bytes: bytes) -> str:
    catalog_object = re.search(rb"\n(\d+)\s+0\s+obj\s*<<.*?/Type\s*/Catalog.*?>>", bytes, re.DOTALL)
    if not catalog_object:
        raise ValueError("Catalog not found")
    end_of_catalog_object = bytes.find(b"endobj", catalog_object.start())
    content_of_catalog_object = bytes[catalog_object.start() : end_of_catalog_object]
    page_count = re.search(rb"/Pages\s+(\d+)\s+0\s+R", content_of_catalog_object)
    if not page_count:
        page_count = re.search(rb"/Pages\s+(\d+)\s+0\s+R", bytes)
        if not page_count:
            raise ValueError("/Pages not found")
    return f"{int(page_count.group(1))} 0 R"


def _scan_pdf_to_get_its_data(initial_content: bytes) -> PdfInfo:
    return PdfInfo(
        content=initial_content,
        startxref=_find_startxref(initial_content),
        max_obj=_get_max_obj_num(initial_content),
        pages_ref=_extract_pages_ref(initial_content),
    )


def _xref_entry(offset: int) -> bytes:
    return f"{offset:010d} 00000 n \n".encode("ascii")


def emplace_manifest_into_pdf(
    initial_content: bytes,
    manifests: ManifestStore,
    *,
    author: str | None = None,
) -> bytes:
    """
    Incrementally adds C2PA Manifest Store to PDF.
    - Exception c2pa.hash.data: start == len(initial_content), length == length of the entire tail (see C2PA 2.2).
    - Sign the claim, build the jumbf store, place it as EmbeddedFile, write xref/trailer correctly.
    """
    try:
        info = _scan_pdf_to_get_its_data(initial_content)
    except ValueError:
        initial_content = _read_pdf_using_pypdf(initial_content=initial_content)
        info = _scan_pdf_to_get_its_data(initial_content)
    initial_length_of_file = len(initial_content)
    pointer_on_previous_xref = info.startxref
    starting_value = info.max_obj + 1

    subtype = "/application#2Fc2pa"
    fname = "manifest.c2pa"

    author_info_required = bool(author)

    assumed_hash_data_len = 0
    last = -1
    for _ in range(RETRY_SIGNATURE):
        manifests.set_hash_data_length_for_all(assumed_hash_data_len)
        store = manifests.serialize()
        length_of_c2pa_manifest = len(store)

        object_1 = (
            f"{starting_value} 0 obj\n".encode("ascii")
            + f"<< /Type /EmbeddedFile /Subtype {subtype} /Length {length_of_c2pa_manifest} >>\n".encode("ascii")
            + b"stream\n"
            + store
            + b"\nendstream\nendobj\n"
        )
        object_2 = (
            f"{starting_value + 1} 0 obj\n".encode("ascii")
            + (
                f"<< /Type /Filespec /AFRelationship /C2PA_Manifest "
                f"/F ({fname}) /UF ({fname}) /Desc (C2PA Manifest Store) "
                f"/Subtype {subtype} /EF << /F {starting_value} 0 R >> >>\n"
            ).encode("ascii")
            + b"endobj\n"
        )
        object_3 = (
            f"{starting_value + 2} 0 obj\n".encode("ascii")
            + f"<< /Type /Names /Names [ ({fname}) {starting_value + 1} 0 R ] >>\n".encode("ascii")
            + b"endobj\n"
        )
        object_4 = (
            f"{starting_value + 3} 0 obj\n".encode("ascii")
            + f"<< /Type /Names /EmbeddedFiles {starting_value + 2} 0 R >>\n".encode("ascii")
            + b"endobj\n"
        )
        object_5 = (
            f"{starting_value + 4} 0 obj\n".encode("ascii")
            + (
                f"<< /Type /Catalog /Pages {info.pages_ref} /Names "
                f"{starting_value + 3} 0 R /AF [ {starting_value + 1} 0 R ] >>\n"
            ).encode("ascii")
            + b"endobj\n"
        )

        if author_info_required:
            author_s = author.replace(")", r"\)") if author else ""
            object_6 = (
                f"{starting_value + 5} 0 obj\n".encode("ascii")
                + f"<< /Author ({author_s}) >>\n".encode("ascii")
                + b"endobj\n"
            )
        else:
            object_6 = b""

        sep = b"\n"
        offset_of_object_1 = initial_length_of_file + len(sep)
        offset_of_object_2 = offset_of_object_1 + len(object_1)
        offset_of_object_3 = offset_of_object_2 + len(object_2)
        offset_of_object_4 = offset_of_object_3 + len(object_3)
        offset_of_object_5 = offset_of_object_4 + len(object_4)
        if author_info_required:
            offset_of_object_6 = offset_of_object_5 + len(object_5)
            xref_pos = offset_of_object_6 + len(object_6)
        else:
            xref_pos = offset_of_object_5 + len(object_5)

        count = 5 + (1 if author_info_required else 0)
        xref = b"xref\n" + f"{starting_value} {count}\n".encode("ascii")
        xref += (
            _xref_entry(offset_of_object_1)
            + _xref_entry(offset_of_object_2)
            + _xref_entry(offset_of_object_3)
            + _xref_entry(offset_of_object_4)
            + _xref_entry(offset_of_object_5)
        )
        if author_info_required:
            xref += _xref_entry(offset_of_object_6)

        size_val = starting_value + count
        trailer = (
            b"trailer\n<< "
            + f"/Size {size_val} ".encode("ascii")
            + f"/Root {starting_value + 4} 0 R ".encode("ascii")
            + f"/Prev {pointer_on_previous_xref} ".encode("ascii")
        )
        if author_info_required:
            trailer += f"/Info {starting_value + 5} 0 R ".encode("ascii")
        trailer += b">>\n"

        tail = (
            sep
            + object_1
            + object_2
            + object_3
            + object_4
            + object_5
            + object_6
            + xref
            + trailer
            + b"startxref\n"
            + str(xref_pos).encode("ascii")
            + b"\n%%EOF\n"
        )

        total_len = len(tail)
        if total_len == last:
            return initial_content + tail
        last = total_len
        assumed_hash_data_len = total_len

    manifests.set_hash_data_length_for_all(assumed_hash_data_len)
    store = manifests.serialize()
    return initial_content + tail
