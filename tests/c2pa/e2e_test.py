import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from c2pie.signing import sign_file
from c2pie.utils.content_types import C2PA_ContentTypes

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

test_files_by_extension = {
    "pdf": [
        "test_doc.pdf",
        "test_doc2.pdf",
    ],
    "jpg": [
        "test_image.jpg",
    ],
}


def get_fixture_full_path(filename: str) -> Path:
    path = FIXTURES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return path


def copy_fixture(source_path: str, destination_path: Path) -> None:
    source_full_path = get_fixture_full_path(source_path)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_full_path, destination_path)


def has_c2patool() -> bool:
    return shutil.which("c2patool") is not None


def _c2pa_json_report(asset_path: str) -> dict:
    """
    Return c2patool's JSON report. If parsing fails, raise with stdout/stderr for debugging.
    """
    c2patool_launch_command = ["c2patool", asset_path, "-d"]

    cp2atool_result = subprocess.run(c2patool_launch_command, capture_output=True, text=True)
    evaluation_result = cp2atool_result
    if cp2atool_result.returncode == 0:
        return json.loads(cp2atool_result.stdout or "{}")
    pytest.fail(
        "c2patool failed or did not output JSON.\n"
        f"args={evaluation_result.args if evaluation_result else None}\n"
        f"stdout={evaluation_result.stdout if evaluation_result else None}\n"
        f"stderr={evaluation_result.stderr if evaluation_result else None}"
    )


@pytest.mark.e2e
def test_e2e_signing_with_c2patool_validation(tmp_path):
    if not has_c2patool():
        pytest.skip("c2patool not available")
    if sign_file is None:
        pytest.skip("sign_file function not available yet")

    os.environ["C2PA_BACKEND"] = "tool"

    for content_type in C2PA_ContentTypes:
        input_file = tmp_path / f"in.{content_type.name}"
        output_file = tmp_path / f"out.{content_type.name}"

        for test_file in test_files_by_extension[content_type.name]:
            copy_fixture(f"./{test_file}", input_file)

            try:
                sign_file(
                    file_type=content_type,
                    input_path=input_file,
                    output_path=output_file,
                )
            except NotImplementedError:
                pytest.xfail("sign_file function not implemented yet")

            data = _c2pa_json_report(str(output_file))
            assert "manifests" in data or "manifest" in data

            manifests = data.get("manifests")
            assert manifests, "no manifests in output"

            if isinstance(manifests, dict):
                manifests_list = list(manifests.values())
            else:
                manifests_list = manifests

            assert manifests_list, "empty manifests list after normalization"
