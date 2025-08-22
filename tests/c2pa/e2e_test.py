import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from test_application.jpeg_test_app import sign_image
from test_application.pdf_test_app import sign_pdf

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def fixture_path(name: str) -> Path:
    p = FIXTURES_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Fixture not found: {p}")
    return p


def copy_fixture(src_name: str, dst_path: Path) -> None:
    src = fixture_path(src_name)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst_path)


def has_c2patool() -> bool:
    return shutil.which("c2patool") is not None


def _c2pa_json_report(asset_path: str) -> dict:
    """
    Return c2patool's JSON report. Try default output first, then detailed (-d).
    If parsing fails, raise with stdout/stderr for debugging.
    """
    variants = (
        ["c2patool", asset_path],
        ["c2patool", asset_path, "-d"],
    )
    last = None
    for args in variants:
        cp2atool_result = subprocess.run(args, capture_output=True, text=True)
        last = cp2atool_result
        if cp2atool_result.returncode == 0:
            try:
                return json.loads(cp2atool_result.stdout or "{}")
            except Exception:
                continue
    pytest.fail(
        "c2patool failed or did not output JSON.\n"
        f"args={last.args if last else None}\n"
        f"stdout={last.stdout if last else None}\n"
        f"stderr={last.stderr if last else None}"
    )


@pytest.mark.e2e
def test_jpeg_e2e_c2patool(tmp_path):
    if not has_c2patool():
        pytest.skip("c2patool not available")
    if sign_image is None:
        pytest.skip("sign_image not available")

    os.environ["C2PA_BACKEND"] = "tool"

    inp = tmp_path / "in.jpg"
    out = tmp_path / "out.jpg"
    copy_fixture("./test_image.jpg", inp)

    try:
        sign_image(
            input_path=inp,
            output_path=out,
        )
    except NotImplementedError:
        pytest.xfail("sign_image not implemented yet")

    data = _c2pa_json_report(str(out))
    assert "manifests" in data or "manifest" in data


@pytest.mark.e2e
def test_pdf_e2e_c2patool(tmp_path):
    if not has_c2patool():
        pytest.skip("c2patool not available")
    if sign_pdf is None:
        pytest.skip("sign_pdf not available yet")

    os.environ["C2PA_BACKEND"] = "tool"

    inp = tmp_path / "in.pdf"
    out = tmp_path / "out.pdf"
    copy_fixture("./test_doc.pdf", inp)

    try:
        sign_pdf(
            input_path=inp,
            output_path=out,
        )
    except NotImplementedError:
        pytest.xfail("sign_pdf not implemented yet")

    data = _c2pa_json_report(str(out))
    assert "manifests" in data or "manifest" in data

    manifests = data.get("manifests")
    assert manifests, "no manifests in output"

    if isinstance(manifests, dict):
        manifests_list = list(manifests.values())
    else:
        manifests_list = manifests

    assert manifests_list, "empty manifests list after normalization"
