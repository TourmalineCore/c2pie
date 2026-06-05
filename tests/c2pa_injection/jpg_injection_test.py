import struct

from c2pie.c2pa_injection.jpg_injection import strip_c2pa_app11_segments
from c2pie.c2pa_parsing.manifest_extractor import extract_manifest_store_bytes_and_ranges_from_jpeg
from tests.helpers.jumbf_generators import _mock_make_app11, _mock_make_jpeg

C2PA_MARK = b"urn:c2pa:"
OTHER_DATA = b"some_other_jumbf_data"


def _strip(jpeg_bytes: bytes) -> bytes:
    """Scan for C2PA segment ranges, then splice them out — the signing pipeline flow."""
    _, ranges = extract_manifest_store_bytes_and_ranges_from_jpeg(jpeg_bytes)

    return strip_c2pa_app11_segments(jpeg_bytes, ranges)


class TestStripC2paApp11Segments:
    def test_jpeg_without_app11_is_unchanged(self):
        jpeg = _mock_make_jpeg()

        assert _strip(jpeg) == jpeg

    def test_non_c2pa_app11_is_preserved(self):
        jpeg = _mock_make_jpeg(
            _mock_make_app11(1, 1, OTHER_DATA),
        )

        assert _strip(jpeg) == jpeg

    def test_c2pa_app11_is_removed(self):
        c2pa_seg = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"manifest_data",
        )

        jpeg = _mock_make_jpeg(c2pa_seg)
        result = _strip(jpeg)

        assert b"\xff\xeb" not in result

    def test_non_jpeg_bytes_between_markers_preserved(self):
        c2pa_seg = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"manifest",
        )

        jpeg = b"\xff\xd8" + b"image_data" + c2pa_seg + b"more_image_data" + b"\xff\xd9"
        result = _strip(jpeg)

        assert b"image_data" in result
        assert b"more_image_data" in result
        assert C2PA_MARK not in result

    def test_multi_segment_c2pa_group_all_removed(self):
        seg1 = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"part_one",
        )

        seg2 = _mock_make_app11(
            1,
            2,
            b"part_two",
        )

        jpeg = _mock_make_jpeg(
            seg1,
            seg2,
        )

        result = _strip(jpeg)

        assert b"\xff\xeb" not in result

    def test_only_c2pa_group_removed_when_mixed(self):
        c2pa_seg = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"manifest",
        )

        other_seg = _mock_make_app11(
            2,
            1,
            OTHER_DATA,
        )

        jpeg = _mock_make_jpeg(
            c2pa_seg,
            other_seg,
        )

        result = _strip(jpeg)

        assert C2PA_MARK not in result
        assert OTHER_DATA in result

    def test_multiple_c2pa_groups_with_different_en_all_removed(self):
        seg_a = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"first_store",
        )

        seg_b = _mock_make_app11(
            2,
            1,
            C2PA_MARK + b"second_store",
        )

        jpeg = _mock_make_jpeg(seg_a, seg_b)
        result = _strip(jpeg)

        assert C2PA_MARK not in result

    def test_result_retains_soi_and_eoi_markers(self):
        c2pa_seg = _mock_make_app11(
            1,
            1,
            C2PA_MARK + b"manifest",
        )

        jpeg = _mock_make_jpeg(c2pa_seg)
        result = _strip(jpeg)

        assert result[:2] == b"\xff\xd8"
        assert result[-2:] == b"\xff\xd9"

    def test_empty_bytes_returns_empty(self):
        assert _strip(b"") == b""

    def test_c2pa_mark_inside_non_jp_app11_not_stripped(self):
        # APP11 without "JP" prefix — not a JUMBF segment, must not be touched.
        payload = b"XX" + struct.pack(">HI", 1, 1) + C2PA_MARK + b"data"
        seg_len = len(payload) + 2
        seg = b"\xff\xeb" + struct.pack(">H", seg_len) + payload
        jpeg = _mock_make_jpeg(seg)
        result = _strip(jpeg)

        assert result == jpeg


class TestStripC2paApp11SegmentsWithExplicitRanges:
    def test_empty_ranges_returns_data_unchanged(self):
        data = b"\xff\xd8somedata\xff\xd9"

        assert strip_c2pa_app11_segments(data, []) == data

    def test_single_range_spliced_out(self):
        assert (
            strip_c2pa_app11_segments(
                b"AAA__BBB",
                [
                    (3, 5),
                ],
            )
            == b"AAABBB"
        )

    def test_multiple_ranges_spliced_out(self):
        data = b"keep1_CUT_keep2_CUT2_keep3"

        assert (
            strip_c2pa_app11_segments(
                data,
                [
                    (5, 9),
                    (15, 20),
                ],
            )
            == b"keep1_keep2_keep3"
        )
