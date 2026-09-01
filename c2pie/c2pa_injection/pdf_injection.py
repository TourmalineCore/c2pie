import re
from io import BytesIO
from typing import NamedTuple

from pypdf import PdfWriter

from c2pie.c2pa.manifest_store import ManifestStore


# More about incremental updates PDF and embedding C2PA Manifest on it,
# described in docs/PDF-structure-overview.md
class PdfInfo(NamedTuple):
    """Structural metadata extracted from an existing PDF, needed to append
    a valid incremental update (new xref table linked via /Prev)."""

    content: bytes
    startxref: int
    max_obj: int
    pages_ref: str


def _read_pdf_using_pypdf(initial_content: bytes) -> bytes:
    """
    Rewrites a malformed/non-standard PDF into a clean, fully parseable PDF
    using pypdf.
    """
    input_stream = BytesIO(initial_content)
    output_stream = BytesIO()
    pdf_writer = PdfWriter(input_stream)
    pdf_writer.write(output_stream)
    output_stream.seek(0)
    byte_string = output_stream.read()
    return byte_string


def _find_startxref(bytes: bytes) -> int:
    """
    Locates the byte offset of the xref table referenced by the LAST
    'startxref ... %%EOF' block in the file.
    """
    patterns = list(re.finditer(rb"startxref\s+(\d+)\s*%%EOF\s*$", bytes, re.DOTALL))
    if not patterns:
        raise ValueError("startxref not found")
    return int(patterns[-1].group(1))


def _get_max_obj_num(bytes: bytes) -> int:
    """
    Scans all 'N 0 obj' declarations in the file and returns the highest
    object number found.
    """
    object_numbers = [int(m.group(1)) for m in re.finditer(rb"\n(\d+)\s+0\s+obj\b", bytes)]
    return max(object_numbers) if object_numbers else 0


def _extract_pages_ref(bytes: bytes) -> str:
    """
    Finds the /Pages indirect reference inside the existing /Catalog object,
    so the new /Catalog object we create for the incremental update points
    to the SAME page tree as the original document.
    """
    catalog_object = re.search(rb"\n(\d+)\s+0\s+obj\s*<<.*?/Type\s*/Catalog.*?>>", bytes, re.DOTALL)
    if not catalog_object:
        raise ValueError("Catalog not found")
    end_of_catalog_object = bytes.find(b"endobj", catalog_object.start())
    content_of_catalog_object = bytes[catalog_object.start() : end_of_catalog_object]
    page_count = re.search(rb"/Pages\s+(\d+)\s+0\s+R", content_of_catalog_object)
    if not page_count:
        # Fallback: some PDFs split Catalog attributes across multiple
        # objects/streams, so /Pages might not be inside the matched
        # Catalog dict. Retry a global search over the whole file.
        page_count = re.search(rb"/Pages\s+(\d+)\s+0\s+R", bytes)
        if not page_count:
            raise ValueError("/Pages not found")
    return f"{int(page_count.group(1))} 0 R"


def _scan_pdf_to_get_its_data(initial_content: bytes) -> PdfInfo:
    """Aggregates all structural info required to append a C2PA incremental
    update: last xref offset, next free object number, and /Pages reference."""
    return PdfInfo(
        content=initial_content,
        startxref=_find_startxref(initial_content),
        max_obj=_get_max_obj_num(initial_content),
        pages_ref=_extract_pages_ref(initial_content),
    )


def _xref_entry(offset: int) -> bytes:
    """
    Formats a single xref table entry per the PDF spec:
    10-digit byte offset + 5-digit generation number + 'n' (in-use) flag.
    """
    return f"{offset:010d} 00000 n \n".encode("ascii")


def prepare_pdf_bytes(content: bytes) -> bytes:
    """
    Returns the PDF bytes ready for signing repaired via pypdf if the raw
    bytes lack a parseable structure.

    Must be called before hashing so that the hash and cai_offset are
    computed against the same byte sequence that will be written to disk.
    """
    try:
        _scan_pdf_to_get_its_data(content)
        return content
    except ValueError:
        repaired = _read_pdf_using_pypdf(content)
        return repaired


def emplace_manifest_into_pdf(
    initial_content: bytes,
    manifest_store: ManifestStore,
    c2pa_offset: int,
    *,
    author: str | None = None,
) -> bytes:
    """
    Incrementally adds C2PA Manifest Store to PDF.
    - Exception c2pa.hash.data: start == len(initial_content), length == length of the entire tail (see C2PA 2.2).
    - Sign the claim, build the jumbf store, place it as EmbeddedFile, write xref/trailer correctly.
    """
    info = _scan_pdf_to_get_its_data(initial_content)

    initial_length_of_file = len(initial_content)
    pointer_on_previous_xref = info.startxref
    starting_value = info.max_obj + 1

    subtype = "/application#2Fc2pa"
    fname = "manifest.c2pa"

    author_info_required = bool(author)

    serialized_manifest_store = manifest_store.serialize()

    serialized_manifest_store_length = len(serialized_manifest_store)

    # Creating Body
    # Object 1: the actual C2PA Manifest Store, embedded as a PDF stream
    # (EmbeddedFile), so the JUMBF bytes travel unmodified inside the PDF.
    object_1 = (
        f"{starting_value} 0 obj\n".encode("ascii")
        + f"<< /Type /EmbeddedFile /Subtype {subtype} /Length {serialized_manifest_store_length} >>\n".encode("ascii")
        + b"stream\n"
        + serialized_manifest_store
        + b"\nendstream\nendobj\n"
    )
    # Object 2: Filespec describing the embedded file, tagged with
    # /AFRelationship /C2PA_Manifest so C2PA-aware readers can find it.
    object_2 = (
        f"{starting_value + 1} 0 obj\n".encode("ascii")
        + (
            f"<< /Type /Filespec /AFRelationship /C2PA_Manifest "
            f"/F ({fname}) /UF ({fname}) /Desc (C2PA Manifest Store) "
            f"/Subtype {subtype} /EF << /F {starting_value} 0 R >> >>\n"
        ).encode("ascii")
        + b"endobj\n"
    )
    # Object 3: a /Names name-tree entry mapping "manifest.c2pa" -> Filespec,
    # required by the PDF EmbeddedFiles mechanism.
    object_3 = (
        f"{starting_value + 2} 0 obj\n".encode("ascii")
        + f"<< /Type /Names /Names [ ({fname}) {starting_value + 1} 0 R ] >>\n".encode("ascii")
        + b"endobj\n"
    )
    # Object 4: the top-level /Names dictionary that exposes our name-tree
    # under /EmbeddedFiles (referenced from the new Catalog below).
    object_4 = (
        f"{starting_value + 3} 0 obj\n".encode("ascii")
        + f"<< /Type /Names /EmbeddedFiles {starting_value + 2} 0 R >>\n".encode("ascii")
        + b"endobj\n"
    )
    # Object 5: a new Catalog object replacing the original one. Reuses the
    # original /Pages tree, adds our /Names (EmbeddedFiles) and lists the
    # Filespec under /AF (Associated Files) so viewers surface the C2PA data.
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
        # Optional object 6: /Info dictionary with /Author, only written if the
        # caller explicitly requested author metadata to be embedded.
        object_6 = (
            f"{starting_value + 5} 0 obj\n".encode("ascii")
            + f"<< /Author ({author_s}) >>\n".encode("ascii")
            + b"endobj\n"
        )
    else:
        object_6 = b""

    # Compute byte offsets of every new object for the xref table
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
    # Creating new xref table
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
    # Creating trailer
    trailer = (
        b"trailer\n<< "
        + f"/Size {size_val} ".encode("ascii")
        + f"/Root {starting_value + 4} 0 R ".encode("ascii")
        + f"/Prev {pointer_on_previous_xref} ".encode("ascii")
    )

    if author_info_required:
        trailer += f"/Info {starting_value + 5} 0 R ".encode("ascii")

    trailer += b">>\n"

    # Assemble the full incremental update tail (first pass)
    # This first tail is only used to measure its exact byte length, so we
    # can tell the hard-binding hash assertion exactly how many trailing
    # bytes to exclude from the file hash (they contain the manifest itself
    # and therefore cannot be part of what the manifest hashes).
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

    manifest_store.add_full_c2pa_structure_exclusion(
        c2pa_offset,
        len(tail),
    )

    # Reserialize manifest_store now that its internal pad
    # has been adjusted, and rebuild object_1 (and thus the whole tail) with
    # the final, correct bytes. All offsets/xref/trailer above are reused
    # as-is, since exclusion pad adjustments are designed to keep the total
    # serialized length of the manifest constant so object_1's length
    # (and every offset that depends on it) does not change.

    serialized_manifest_store = manifest_store.serialize()
    serialized_manifest_store_length = len(serialized_manifest_store)

    object_1 = (
        f"{starting_value} 0 obj\n".encode("ascii")
        + f"<< /Type /EmbeddedFile /Subtype {subtype} /Length {serialized_manifest_store_length} >>\n".encode("ascii")
        + b"stream\n"
        + serialized_manifest_store
        + b"\nendstream\nendobj\n"
    )

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

    return initial_content + tail
