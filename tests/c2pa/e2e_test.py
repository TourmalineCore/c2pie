import json
import shutil
import subprocess
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from c2pie.signing import sign_file

FILES_DIR = Path(__file__).parent.parent / "fixtures"

test_cases = [
    (
        Path(FILES_DIR / "test_image.jpg"),
        Path(FILES_DIR / "schemas/test_image_jpg.schema.json"),
    ),
    (
        Path(FILES_DIR / "test_image.jpeg"),
        Path(FILES_DIR / "schemas/test_image_jpeg.schema.json"),
    ),
    (
        Path(FILES_DIR / "test_doc.pdf"),
        Path(FILES_DIR / "schemas/test_doc_pdf.schema.json"),
    ),
    (
        Path(FILES_DIR / "test_doc2.pdf"),
        Path(FILES_DIR / "schemas/test_doc2_pdf.schema.json"),
    ),
]


def _has_c2patool() -> bool:
    return shutil.which("c2patool") is not None


def _sign_file_with_mock_uuids(
    data_file: Path,
    output_file: Path,
):
    fixed_uuid = uuid.UUID("47affab1a5d24c75b991fbc030e02448")

    # If the call is not intercepted and a fixed value
    # is not specified, a random value will be generated
    with (
        patch("c2pie.interface.uuid.uuid4", return_value=fixed_uuid),
        patch("c2pie.c2pa.claim.uuid.uuid4", return_value=fixed_uuid),
    ):
        sign_file(
            input_path=data_file,
            output_path=output_file,
        )


def _validate_using_c2patool_and_return_json_report(asset_path: Path) -> dict:
    """
    Return c2patool's JSON report. If parsing fails, raise with stdout/stderr for debugging.
    """
    c2patool_launch_command = ["c2patool", asset_path, "-d"]

    c2patool_result = subprocess.run(
        c2patool_launch_command,
        # If set to False (by default), 'stdout' and 'stderr' outputs
        # will not be available via '.stderr' and '.stdout', correspondingly.
        capture_output=True,
        # If set to False (by default), a byte stream will be
        # returned instead of a string.
        text=True,
    )

    if c2patool_result.returncode == 0:
        return json.loads(c2patool_result.stdout)

    pytest.fail(
        "c2patool failed or did not output JSON.\n"
        f"args={c2patool_result.args if c2patool_result else None}\n"
        f"stdout={c2patool_result.stdout if c2patool_result else None}\n"
        f"stderr={c2patool_result.stderr if c2patool_result else None}"
    )


@pytest.mark.parametrize(
    "data_file,schema_file",
    test_cases,
    ids=lambda p: p.name,
)
def test_e2e_signing_with_c2patool_validation(
    data_file: Path,
    schema_file: Path,
    tmp_path,
):
    if not _has_c2patool():
        pytest.skip("c2patool not available")

    output_file = tmp_path / f"out{data_file.suffix}"

    _sign_file_with_mock_uuids(
        data_file,
        output_file,
    )

    report = _validate_using_c2patool_and_return_json_report(output_file)
    manifests = report.get("manifests")
    expected_schema = json.loads(schema_file.read_text())

    assert manifests == expected_schema


# @pytest.mark.parametrize(
#     "iteration",
#     range(100),
# )
# def test_e2e_signature_stability(iteration, tmp_path):
#     if not _has_c2patool():
#         pytest.skip("c2patool not available")

#     data_file = Path(FILES_DIR / "test_image.jpg")
#     output_file = tmp_path / f"out{data_file.suffix}"

#     _sign_file_with_mock_uuids(
#         data_file,
#         output_file,
#     )

#     report = _validate_using_c2patool_and_return_json_report(output_file)
#     validation_state = report.get("validation_state")

#     assert validation_state == "Valid"
