from __future__ import annotations

import re
from typing import NamedTuple

from c2pie.c2pa.config import RETRY_SIGNATURE
from c2pie.c2pa.manifest_store import ManifestStore


class PdfInfo(NamedTuple):
    buf: bytes
    startxref: int
    max_obj: int
    pages_ref: str


def _find_startxref(b: bytes) -> int:
    m = list(re.finditer(rb"startxref\s+(\d+)\s*%%EOF\s*$", b, re.DOTALL))
    if not m:
        raise ValueError("startxref not found")
    return int(m[-1].group(1))


def _max_obj_num(b: bytes) -> int:
    nums = [int(m.group(1)) for m in re.finditer(rb"\n(\d+)\s+0\s+obj\b", b)]
    return max(nums) if nums else 0


def _extract_pages_ref(b: bytes) -> str:
    mcat = re.search(rb"\n(\d+)\s+0\s+obj\s*<<.*?/Type\s*/Catalog.*?>>", b, re.DOTALL)
    if not mcat:
        raise ValueError("Catalog not found")
    end = b.find(b"endobj", mcat.start())
    segment = b[mcat.start() : end]
    mp = re.search(rb"/Pages\s+(\d+)\s+0\s+R", segment)
    if not mp:
        mp = re.search(rb"/Pages\s+(\d+)\s+0\s+R", b)
        if not mp:
            raise ValueError("/Pages not found")
    return f"{int(mp.group(1))} 0 R"


def _scan(b: bytes) -> PdfInfo:
    return PdfInfo(
        buf=b,
        startxref=_find_startxref(b),
        max_obj=_max_obj_num(b),
        pages_ref=_extract_pages_ref(b),
    )


def _xref_entry(off: int) -> bytes:
    return f"{off:010d} 00000 n \n".encode("ascii")


def emplace_manifest_into_pdf(base: bytes, manifests: ManifestStore, *, author: str | None = None) -> bytes:
    """
    Incrementally adds C2PA Manifest Store to PDF.
    - Exception c2pa.hash.data: start == len(base), length == length of the entire tail (see C2PA 2.2).
    - Sign the claim, build the jumbf store, place it as EmbeddedFile, write xref/trailer correctly.
    """
    info = _scan(base)
    base_len = len(base)
    prev = info.startxref
    n0 = info.max_obj + 1

    subtype = "/application#2Fc2pa"
    fname = "manifest.c2pa"

    want_info = bool(author)

    guess = 0
    last = -1
    for _ in range(RETRY_SIGNATURE):
        manifests.set_hash_data_length_for_all(guess)
        store = manifests.serialize()
        L = len(store)

        objN = (
            f"{n0} 0 obj\n".encode("ascii")
            + f"<< /Type /EmbeddedFile /Subtype {subtype} /Length {L} >>\n".encode("ascii")
            + b"stream\n"
            + store
            + b"\nendstream\nendobj\n"
        )
        objN1 = (
            f"{n0 + 1} 0 obj\n".encode("ascii")
            + (
                f"<< /Type /Filespec /AFRelationship /C2PA_Manifest "
                f"/F ({fname}) /UF ({fname}) /Desc (C2PA Manifest Store) "
                f"/Subtype {subtype} /EF << /F {n0} 0 R >> >>\n"
            ).encode("ascii")
            + b"endobj\n"
        )
        objN2 = (
            f"{n0 + 2} 0 obj\n".encode("ascii")
            + f"<< /Type /Names /Names [ ({fname}) {n0 + 1} 0 R ] >>\n".encode("ascii")
            + b"endobj\n"
        )
        objN3 = (
            f"{n0 + 3} 0 obj\n".encode("ascii")
            + f"<< /Type /Names /EmbeddedFiles {n0 + 2} 0 R >>\n".encode("ascii")
            + b"endobj\n"
        )
        objN4 = (
            f"{n0 + 4} 0 obj\n".encode("ascii")
            + (f"<< /Type /Catalog /Pages {info.pages_ref} /Names {n0 + 3} 0 R /AF [ {n0 + 1} 0 R ] >>\n").encode(
                "ascii"
            )
            + b"endobj\n"
        )

        if want_info:
            author_s = author.replace(")", r"\)") if author else ""
            objN5 = f"{n0 + 5} 0 obj\n".encode("ascii") + f"<< /Author ({author_s}) >>\n".encode("ascii") + b"endobj\n"
        else:
            objN5 = b""

        sep = b"\n"
        offN = base_len + len(sep)
        offN1 = offN + len(objN)
        offN2 = offN1 + len(objN1)
        offN3 = offN2 + len(objN2)
        offN4 = offN3 + len(objN3)
        if want_info:
            offN5 = offN4 + len(objN4)
            xref_pos = offN5 + len(objN5)
        else:
            xref_pos = offN4 + len(objN4)

        count = 5 + (1 if want_info else 0)
        xref = b"xref\n" + f"{n0} {count}\n".encode("ascii")
        xref += _xref_entry(offN) + _xref_entry(offN1) + _xref_entry(offN2) + _xref_entry(offN3) + _xref_entry(offN4)
        if want_info:
            xref += _xref_entry(offN5)

        size_val = n0 + count
        trailer = (
            b"trailer\n<< "
            + f"/Size {size_val} ".encode("ascii")
            + f"/Root {n0 + 4} 0 R ".encode("ascii")
            + f"/Prev {prev} ".encode("ascii")
        )
        if want_info:
            trailer += f"/Info {n0 + 5} 0 R ".encode("ascii")
        trailer += b">>\n"

        tail = (
            sep
            + objN
            + objN1
            + objN2
            + objN3
            + objN4
            + objN5
            + xref
            + trailer
            + b"startxref\n"
            + str(xref_pos).encode("ascii")
            + b"\n%%EOF\n"
        )

        total_len = len(tail)
        if total_len == last:
            return base + tail
        last = total_len
        guess = total_len

    manifests.set_hash_data_length_for_all(guess)
    store = manifests.serialize()
    return base + tail
