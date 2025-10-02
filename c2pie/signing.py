import hashlib
import os
from pathlib import Path

from c2pie.interface import (
    C2PA_AssertionTypes,
    TC_C2PA_EmplaceManifest,
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
)
from c2pie.utils.content_types import C2PA_ContentTypes

creative_work_schema = {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "author": [{"@type": "Organization", "name": "Tourmaline Core"}],
    "copyrightYear": "2026",
    "copyrightHolder": "c2pie",
}


def _ensure_path_type_for_filepath(path: str | Path) -> Path:
    if type(path) is not Path:
        return Path(path)
    return path


def _get_content_type_by_filepath(file_path: Path) -> C2PA_ContentTypes:
    file_content_type = C2PA_ContentTypes(file_path.suffix)
    return file_content_type


def _ensure_path_correctness(file_path: Path) -> None:
    supported_extensions: list[str] = [_type.value for _type in C2PA_ContentTypes]
    # check if input_file_path isn't a directory
    if file_path.is_dir():
        raise ValueError(f"The provided path is a directory, not a file: {file_path}.")

    # check if file has one of the supported extensions
    file_extension = file_path.suffix
    if file_extension not in supported_extensions:
        raise ValueError(
            f"The file has an incorrect extension: {file_extension}"
            f" Currently, only the following extensions are supported: {supported_extensions}.",
        )


def _validate_input_and_output_paths(
    input_file_path: Path | str,
    output_file_path: Path | str | None,
) -> tuple[Path, Path]:
    input_file_path = _ensure_path_type_for_filepath(path=input_file_path)

    if not input_file_path.exists():
        raise ValueError(f"Cannot find the provided path: {input_file_path}.")

    # check if arguments are correct
    _ensure_path_correctness(input_file_path)

    if output_file_path:
        output_file_path = _ensure_path_type_for_filepath(path=output_file_path)
        _ensure_path_correctness(output_file_path)

    # fix output_file_path
    if not output_file_path:
        name_of_input_file = input_file_path.name
        output_file_path = input_file_path.with_name("signed_" + name_of_input_file)

    return input_file_path, output_file_path


def _load_certificates_and_key(
    key_path: str | None,
    certificates_path: str | None,
) -> tuple[bytes, bytes]:
    if not key_path:
        raise ValueError("Key filepath variable has not been set. Cannot sign the provided file.")
    if not certificates_path:
        raise ValueError("Cert filepath variable has not been set. Cannot sign the provided file.")

    with open(key_path, "rb") as f:
        key = f.read()
    with open(certificates_path, "rb") as f:
        certificates = f.read()

    return key, certificates


def sign_file(
    input_path: Path | str,
    output_path: Path | str | None = None,
    key_path: str | None = os.getenv("C2PIE_KEY_FILEPATH"),
    certificates_path: str | None = os.getenv("C2PIE_CERT_FILEPATH"),
) -> None:
    with open(input_path, "rb") as f:
        raw_bytes = f.read()

    key, certificates = _load_certificates_and_key(
        key_path=key_path,
        certificates_path=certificates_path,
    )

    input_path, output_path = _validate_input_and_output_paths(
        input_file_path=input_path,
        output_file_path=output_path,
    )

    file_type: C2PA_ContentTypes = _get_content_type_by_filepath(file_path=input_path)

    if file_type.name == "pdf":
        cai_offset = len(raw_bytes)
    else:
        cai_offset = 2

    creative_work_assertion = TC_C2PA_GenerateAssertion(
        C2PA_AssertionTypes.creative_work,
        creative_work_schema,
    )

    hash_data_assertion = TC_C2PA_GenerateHashDataAssertion(
        cai_offset=cai_offset, hashed_data=hashlib.sha256(raw_bytes).digest()
    )

    assertions = [creative_work_assertion, hash_data_assertion]

    manifest = TC_C2PA_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=certificates,
    )

    signed_bytes = TC_C2PA_EmplaceManifest(
        format_type=file_type,
        content_bytes=raw_bytes,
        c2pa_offset=cai_offset,
        manifests=manifest,
    )

    with open(output_path, "wb") as output_file:
        output_file.write(signed_bytes)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")
