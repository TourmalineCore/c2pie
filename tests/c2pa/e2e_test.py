import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from c2pie.signing import sign_file
from c2pie.utils.content_types import C2PA_ContentTypes

TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"

test_files_by_extension = {
    "pdf": [
        "test_doc.pdf",
        "test_broken_doc.pdf",
    ],
    "jpg": [
        "test_image.jpg",
    ],
    "jpeg": [
        "test_image.jpeg",
    ],
}


def get_test_file_full_path(filename: str) -> Path:
    path = TEST_FILES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")

    return path


def copy_test_file(
    source_path: str,
    destination_path: Path,
) -> None:
    source_full_path = get_test_file_full_path(source_path)

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copyfile(
        source_full_path,
        destination_path,
    )


def has_c2patool() -> bool:
    return shutil.which("c2patool") is not None


def _validate_using_c2patool_and_return_json_report(asset_path: Path) -> dict:
    """
    Return c2patool's JSON report. If parsing fails, raise with stdout/stderr for debugging.
    """
    c2patool_launch_command = ["c2patool", asset_path, "-d"]

    cp2atool_result = subprocess.run(
        c2patool_launch_command,
        # If set to False (by default), 'stdout' and 'stderr' outputs
        # will not be available via '.stderr' and '.stdout', correspondingly.
        capture_output=True,
        # If set to False (by default), a byte stream will be
        # returned instead of a string.
        text=True,
    )

    if cp2atool_result.returncode == 0:
        return json.loads(cp2atool_result.stdout)

    pytest.fail(
        "c2patool failed or did not output JSON.\n"
        f"args={cp2atool_result.args if cp2atool_result else None}\n"
        f"stdout={cp2atool_result.stdout if cp2atool_result else None}\n"
        f"stderr={cp2atool_result.stderr if cp2atool_result else None}"
    )


@pytest.mark.e2e
def test_e2e_signing_with_c2patool_validation(tmp_path):
    if not has_c2patool():
        pytest.skip("c2patool not available")

    if not sign_file:
        pytest.skip("sign_file function not available yet")

    for content_type in C2PA_ContentTypes:
        input_file = tmp_path / f"in.{content_type.name}"
        output_file = tmp_path / f"out.{content_type.name}"

        for test_file in test_files_by_extension[content_type.name]:
            copy_test_file(
                test_file,
                input_file,
            )

            sign_file(
                input_path=input_file,
                output_path=output_file,
            )

            report = _validate_using_c2patool_and_return_json_report(output_file)
            assert "manifests" in report

            manifests = report.get("manifests")
            assert manifests, "no manifests in output"

            manifests_list = list(manifests.values())
            assert manifests_list, "empty manifests list after normalization"


@pytest.mark.e2e
@pytest.mark.parametrize(
    "iteration",
    range(30),
)
def test_e2e_signature_stability(
    iteration,
    tmp_path,
):
    if not has_c2patool():
        pytest.skip("c2patool not available")

    if not sign_file:
        pytest.skip("sign_file function not available yet")

    for content_type in C2PA_ContentTypes:
        input_file = tmp_path / f"in.{content_type.name}"
        output_file = tmp_path / f"out.{content_type.name}"

        for test_file in test_files_by_extension[content_type.name]:
            copy_test_file(
                test_file,
                input_file,
            )

            sign_file(
                input_path=input_file,
                output_path=output_file,
            )

            report = _validate_using_c2patool_and_return_json_report(output_file)
            validation_state = report.get("validation_state")

            assert validation_state == "Valid"


def test_calling_sign_file_with_thumbnail_file_extension_that_is_not_supported_causes_error():
    expected_error_message = (
        "The thumbnail file has an incorrect extension: .pdf. "
        "Currently, only the following extensions are supported: ['.jpeg', '.jpg', '.png']"
    )

    with pytest.raises(
        ValueError,
        match=re.escape(expected_error_message),
    ):
        sign_file(
            input_path=get_test_file_full_path("test_image.jpg"),
            thumbnail_file_path=get_test_file_full_path("test_doc.pdf"),
        )
