import pytest

from c2pie.c2pa_injection.pdf_injection import _extract_pages_ref, _find_startxref, _max_obj_num


def test_find_startxref():
    test_bytes = b"startxref 4 %%EOF "
    assert isinstance(_find_startxref(test_bytes), int)


def test_not_find_startxref():
    test_bytes = b"ercejr4nfjn"
    with pytest.raises(ValueError):
        _find_startxref(test_bytes)


def test_max_obj_num_with_and_without_num():
    test_bytes = b"\n1 0 obj\n5 0 obj\n6 0 obj\n"

    assert _max_obj_num(test_bytes) == 6

    test_bytes = b"startxref 4 %%EOF "
    assert _max_obj_num(test_bytes) == 0


def test_extract_pages_ref_no_catalog():
    test_bytes = b"\n1 0 obj\n5 0 obj\n6 0 obj\n"
    with pytest.raises(ValueError, match="Catalog not found"):
        _extract_pages_ref(test_bytes)


def test_extract_pages_ref_no_pages():
    test_bytes = b"\n1 0 obj \n<</Type /Catalog 2 0 R>>"
    with pytest.raises(ValueError, match="Pages not found"):
        _extract_pages_ref(test_bytes)

