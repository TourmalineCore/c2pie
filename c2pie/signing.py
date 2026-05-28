import hashlib
import os
from pathlib import Path
from typing import Literal

from c2pie.c2pa_injection.pdf_injection import prepare_pdf_bytes
from c2pie.c2pa_parsing.jumbf_parsing import extract_manifest_boxes, get_active_manifest_uuid
from c2pie.c2pa_parsing.manifest_extractor import extract_manifest_store_bytes
from c2pie.interface import (
    c2pie_EmplaceManifest,
    c2pie_GenerateActionsAssertion,
    c2pie_GenerateHashDataAssertion,
    c2pie_GenerateIngredientAssertion,
    c2pie_GenerateManifestStore,
)
from c2pie.jumbf_boxes.box import Box
from c2pie.utils.content_types import C2PA_ContentTypes
from c2pie.utils.generate_hashed_uri_map import generate_hashed_uri_map


def _ensure_path_type_for_filepath(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


def _get_content_type_by_filepath(file_path: Path) -> C2PA_ContentTypes:
    file_content_type = C2PA_ContentTypes(file_path.suffix)
    return file_content_type


_DC_FORMAT_BY_CONTENT_TYPE: dict[str, str] = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "pdf": "application/pdf",
}


def _check_file_extension_is_supported(file_path: Path) -> None:
    supported_extensions: list[str] = [_type.value for _type in C2PA_ContentTypes]
    file_extension = file_path.suffix
    if file_extension not in supported_extensions:
        raise ValueError(
            f"The file has an incorrect extension: {file_extension}"
            f" Currently, only the following extensions are supported: {supported_extensions}.",
        )


def _validate_general_filepath(
    file_path: str | Path,
    file_path_type: Literal["input_file", "output_file", "other"] = "other",
) -> Path:
    if not file_path:
        raise ValueError("File path has not been set")

    ensured_file_path = _ensure_path_type_for_filepath(file_path)

    if file_path_type != "output_file":
        if ensured_file_path.is_dir():
            raise ValueError(f"The provided path is a directory, not a file: {file_path}.")

        if not ensured_file_path.exists():
            raise ValueError(f"Cannot find the provided path: {file_path}.")

    if file_path_type != "other":
        _check_file_extension_is_supported(file_path=ensured_file_path)

    return ensured_file_path


def _validate_input_and_output_filepaths(
    input_file_path: Path | str,
    output_file_path: Path | str | None,
) -> tuple[Path, Path]:
    validated_input_file_path = _validate_general_filepath(
        file_path=input_file_path,
        file_path_type="input_file",
    )

    if output_file_path:
        validated_output_file_path = _validate_general_filepath(
            file_path=output_file_path,
            file_path_type="output_file",
        )

    # set output_file_path if not set
    if not output_file_path:
        name_of_input_file = validated_input_file_path.name
        validated_output_file_path = validated_input_file_path.with_name("signed_" + name_of_input_file)

    return validated_input_file_path, validated_output_file_path


def _load_certificates_and_key(
    key_path: str | None,
    certificates_path: str | None,
) -> tuple[bytes, bytes]:
    key_path = key_path or os.getenv("C2PIE_PRIVATE_KEY_FILE")
    if not key_path:
        raise ValueError("Key filepath variable has not been set. Cannot sign the provided file.")

    certificates_path = certificates_path or os.getenv("C2PIE_CERTIFICATE_CHAIN_FILE")
    if not certificates_path:
        raise ValueError("Certificate filepath variable has not been set. Cannot sign the provided file.")

    validated_key_path = _validate_general_filepath(key_path)
    validated_certificates_path = _validate_general_filepath(certificates_path)

    with open(validated_key_path, "rb") as f:
        key = f.read()
    with open(validated_certificates_path, "rb") as f:
        certificates = f.read()

    return key, certificates


def sign_file(
    input_path: Path | str,
    output_path: Path | str | None = None,
    key_path: str | None = None,
    certificates_path: str | None = None,
    tsa_url: str | None = None,
    require_tsa: bool = False,
    tsa_log_dir: str | None = None,
) -> None:
    key, certificates = _load_certificates_and_key(
        key_path=key_path,
        certificates_path=certificates_path,
    )

    input_path, output_path = _validate_input_and_output_filepaths(
        input_file_path=input_path,
        output_file_path=output_path,
    )

    with open(input_path, "rb") as f:
        raw_bytes = f.read()

    file_type: C2PA_ContentTypes = _get_content_type_by_filepath(input_path)

    if file_type.name == "pdf":
        raw_bytes = prepare_pdf_bytes(raw_bytes)
        cai_offset = len(raw_bytes)
    else:
        cai_offset = 2

    assertions = []

    hash_data_assertion = c2pie_GenerateHashDataAssertion(
        hashed_data=hashlib.sha256(raw_bytes).digest(),
    )

    assertions.append(hash_data_assertion)

    manifest_store_bytes = extract_manifest_store_bytes(
        file_type,
        raw_bytes,
    )

    active_manifest_urn: str | None = get_active_manifest_uuid(manifest_store_bytes)
    previous_manifest_boxes: list[Box] = extract_manifest_boxes(manifest_store_bytes)

    ingredient_assertion = c2pie_GenerateIngredientAssertion(
        title=input_path.name,
        dc_format=_DC_FORMAT_BY_CONTENT_TYPE[file_type.name],
        ingredient_bytes=raw_bytes,
        active_manifest_urn=active_manifest_urn,
        previous_manifest_boxes=previous_manifest_boxes,
    )
    assertions.append(ingredient_assertion)

    ingredient_assertion_hash = hashlib.sha256(ingredient_assertion.payload).digest()

    actions_assertion_parameters: dict[str, list[dict[str, str | bytes]]] = {
        "ingredients": [
            generate_hashed_uri_map(
                url=f"self#jumbf=c2pa.assertions/{ingredient_assertion.get_label()}",
                hash_value=ingredient_assertion_hash,
                hash_algorithm="sha256",
            ),
        ],
    }

    actions_assertion = c2pie_GenerateActionsAssertion(
        action="c2pa.opened",
        parameters=actions_assertion_parameters,
    )
    assertions.append(actions_assertion)

    manifest_store = c2pie_GenerateManifestStore(
        assertions=assertions,
        private_key=key,
        certificate_chain=certificates,
        file_name=output_path.name,
        previous_manifest_boxes=previous_manifest_boxes,
        tsa_url=tsa_url,
        require_tsa=require_tsa,
        tsa_log_dir=tsa_log_dir,
    )

    signed_bytes = c2pie_EmplaceManifest(
        format_type=file_type,
        content_bytes=raw_bytes,
        c2pa_offset=cai_offset,
        manifest_store=manifest_store,
    )

    with open(output_path, "wb") as output_file:
        output_file.write(signed_bytes)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")
