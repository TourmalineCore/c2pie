"""
E2E tests run in two stages, so CI can sign files on every OS/Python
and validate them with several c2patool versions in a separate job:

1. e2e_sign: signs the test files and saves them into SIGNED_DIR.
   The file name prefix (single-, tsa-, double-, ...) tells which checks to run.
2. e2e_validate: validates every file from SIGNED_DIR with c2patool.

Locally run them one after another:
    pytest -m e2e_sign tests/c2pa/e2e_test.py
    pytest -m e2e_validate tests/c2pa/e2e_test.py
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from c2pie.signing import sign_file
from c2pie.tsa.exceptions import TSAConnectionError
from c2pie.utils.content_types import C2PA_ContentTypes

TSA_URL = "http://timestamp.digicert.com"
TEST_FILES_DIR = Path(__file__).parent.parent / "test_files"
SIGNED_DIR = Path(os.getenv("C2PIE_E2E_SIGNED_DIR", Path(tempfile.gettempdir()) / "c2pie-e2e-signed"))
C2PATOOL = os.getenv("C2PATOOL", "c2patool")
STABILITY_ITERATIONS = int(os.getenv("C2PIE_E2E_STABILITY_ITERATIONS", "30"))

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


@pytest.fixture(autouse=True)
def _create_signed_dir():
    SIGNED_DIR.mkdir(parents=True, exist_ok=True)


def has_c2patool() -> bool:
    return shutil.which(C2PATOOL) is not None


def _validate_using_c2patool_and_return_json_report(asset_path: Path) -> dict:
    """
    Return c2patool's JSON report. If parsing fails, raise with stdout/stderr for debugging.
    """
    c2patool_launch_command = [C2PATOOL, asset_path, "-d"]

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
@pytest.mark.e2e_sign
def test_e2e_signing_with_c2patool_validation(tmp_path):
    if not sign_file:
        pytest.skip("sign_file function not available yet")

    for content_type in C2PA_ContentTypes:
        input_file = tmp_path / f"in.{content_type.name}"

        for test_file in test_files_by_extension[content_type.name]:
            output_file = SIGNED_DIR / f"single-{test_file}"

            copy_test_file(
                test_file,
                input_file,
            )

            sign_file(
                input_path=input_file,
                output_path=output_file,
            )


@pytest.mark.e2e
@pytest.mark.e2e_sign
@pytest.mark.parametrize(
    "content_type",
    list(C2PA_ContentTypes),
    ids=lambda ct: ct.name,
)
def test_e2e_signing_with_tsa_produces_valid_file_with_timestamp(content_type, tmp_path):
    test_file = test_files_by_extension[content_type.name][0]
    input_file = tmp_path / f"input.{content_type.name}"
    output_file = SIGNED_DIR / f"tsa-{test_file}"

    copy_test_file(test_file, input_file)

    try:
        sign_file(
            input_path=input_file,
            output_path=output_file,
            tsa_url=TSA_URL,
        )
    except TSAConnectionError:
        pytest.skip(f"TSA server not reachable: {TSA_URL}")


@pytest.mark.e2e
@pytest.mark.e2e_sign
@pytest.mark.parametrize(
    "content_type",
    list(C2PA_ContentTypes),
    ids=lambda ct: ct.name,
)
def test_e2e_double_signing_creates_linked_manifests(
    content_type,
    tmp_path,
):
    for test_file in test_files_by_extension[content_type.name]:
        first_signed = tmp_path / f"first.{content_type.name}"
        second_signed = SIGNED_DIR / f"double-{test_file}"

        copy_test_file(test_file, first_signed)

        sign_file(
            input_path=first_signed,
            output_path=first_signed,
        )

        sign_file(
            input_path=first_signed,
            output_path=second_signed,
        )


@pytest.mark.e2e
@pytest.mark.e2e_sign
@pytest.mark.parametrize(
    "content_type",
    list(C2PA_ContentTypes),
    ids=lambda ct: ct.name,
)
def test_e2e_repeated_signing_produces_single_valid_manifest_store(
    content_type,
):
    """Signing the same file three times must not leave orphaned manifest stores."""
    for file in test_files_by_extension[content_type.name]:
        test_file = file
        signed_file = SIGNED_DIR / f"repeated-{test_file}"

        copy_test_file(
            test_file,
            signed_file,
        )

        for _ in range(3):
            sign_file(
                input_path=signed_file,
                output_path=signed_file,
            )


@pytest.mark.e2e
@pytest.mark.e2e_sign
@pytest.mark.parametrize(
    "iteration",
    range(STABILITY_ITERATIONS),
)
def test_e2e_signature_stability(
    iteration,
    tmp_path,
):
    if not sign_file:
        pytest.skip("sign_file function not available yet")

    for content_type in C2PA_ContentTypes:
        input_file = tmp_path / f"in.{content_type.name}"

        for test_file in test_files_by_extension[content_type.name]:
            output_file = SIGNED_DIR / f"stability-{iteration}-{test_file}"

            copy_test_file(
                test_file,
                input_file,
            )

            sign_file(
                input_path=input_file,
                output_path=output_file,
            )


# Checks of the validation stage. They are the same checks that the signing tests
# above did inline before the split, picked by the prefix of the signed file name.


def _check_single(report: dict) -> None:
    assert "manifests" in report

    manifests = report.get("manifests")
    assert manifests, "no manifests in output"

    manifests_list = list(manifests.values())
    assert manifests_list, "empty manifests list after normalization"


def _check_tsa(report: dict) -> None:
    assert report.get("validation_state") == "Valid"

    active_urn = report["active_manifest"]
    active_manifest = report["manifests"][active_urn]
    assert "time" in active_manifest["signature"]


def _check_double(report: dict) -> None:
    assert report.get("validation_state") == "Valid"

    manifests = report.get("manifests", {})
    assert len(manifests) == 2

    active_urn = report["active_manifest"]
    active_manifest = manifests[active_urn]
    ingredient = active_manifest["assertion_store"]["c2pa.ingredient.v3"]

    assert ingredient["relationship"] == "parentOf"

    previous_urns = [urn for urn in manifests if urn != active_urn]
    assert len(previous_urns) == 1

    previous_urn = previous_urns[0]
    assert previous_urn in ingredient["activeManifest"]["url"]


def _check_repeated(report: dict) -> None:
    assert report.get("validation_state") == "Valid"
    assert len(report.get("manifests", {})) == 3


def _check_stability(report: dict) -> None:
    validation_state = report.get("validation_state")

    assert validation_state == "Valid"


CHECKS_BY_PREFIX = {
    "single": _check_single,
    "tsa": _check_tsa,
    "double": _check_double,
    "repeated": _check_repeated,
    "stability": _check_stability,
}


def _signed_files() -> list[Path]:
    # Recursive search, because in CI each sign job downloads into its own subfolder.
    return sorted(path for path in SIGNED_DIR.rglob("*") if path.is_file())


@pytest.mark.e2e
@pytest.mark.e2e_validate
def test_e2e_signed_files_exist():
    assert _signed_files(), f"No signed files in {SIGNED_DIR}, run the e2e_sign stage first"


@pytest.mark.e2e
@pytest.mark.e2e_validate
@pytest.mark.parametrize(
    "signed_file",
    _signed_files(),
    ids=lambda path: path.relative_to(SIGNED_DIR).as_posix(),
)
def test_e2e_validate_signed_file(signed_file: Path):
    if not has_c2patool():
        pytest.fail(f"c2patool not available: {C2PATOOL}")

    prefix = signed_file.name.split("-")[0]
    report = _validate_using_c2patool_and_return_json_report(signed_file)

    CHECKS_BY_PREFIX[prefix](report)
