from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Literal

from c2pie.interface import (
    C2PA_AssertionTypes,
    c2pie_EmplaceManifest,
    c2pie_GenerateAssertion,
    c2pie_GenerateHashDataAssertion,
    c2pie_GenerateManifest,
)
from c2pie.utils.content_types import C2PA_ContentTypes


def _read_schema_from_file(schema_filepath: Path) -> dict[str]:
    try:
        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
        return schema
    except Exception as ex:
        raise ex


def _validate_schema(schema: dict[str]) -> None:
    expected_items = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
    }

    # check whether the @context and @type properties match the expected values
    for property in ["@context", "@type"]:
        value = schema.get(property, None)
        if value != expected_items[property]:
            raise ValueError(
                "Schema must include the following properties with these values: "
                '{@context: "https://schema.org", "@type": "CreativeWork"}'
            )

    # check that "copyrightYear" and "copyrightHolder" exist
    for property in ["copyrightYear", "copyrightHolder"]:
        value = schema.get(property, None)
        if not value:
            raise ValueError('Schema must include "copyrightYear" and "copyrightHolder"')

    # check that "author" is a non-empty list whose first item has "@type" and "name"
    author = schema.get("author", None)
    if not (isinstance(author, list) and author):
        raise ValueError('author must be a non-empty list of objects with "@type" and "name"')
    else:
        author = author[0]

    author_type = author.get("@type", None)
    author_name = author.get("name", None)

    if not author_type or not author_name:
        raise ValueError('author[@"type"] and author[@"name"] must not be empty')

    if author_type != "Organization" and author_type != "Person":
        raise ValueError('author["@type"] must be "Organization" or "Person"')


def _load_signature_schema(schema_path: str | Path | None) -> dict[str]:
    default_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Organization", "name": "Tourmaline Core"}],
        "copyrightYear": "2026",
        "copyrightHolder": "c2pie",
    }

    if schema_path is None:
        return default_schema

    validated_schema_path = _validate_general_filepath(file_path=schema_path)
    schema = _read_schema_from_file(schema_filepath=validated_schema_path)
    _validate_schema(schema=schema)
    return schema


def _ensure_path_type_for_filepath(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


def _get_content_type_by_filepath(file_path: Path) -> C2PA_ContentTypes:
    file_content_type = C2PA_ContentTypes(file_path.suffix)
    return file_content_type


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
    schema_path: str | None = None,
) -> None:
    key, certificates = _load_certificates_and_key(
        key_path=key_path,
        certificates_path=certificates_path,
    )

    input_path, output_path = _validate_input_and_output_filepaths(
        input_file_path=input_path,
        output_file_path=output_path,
    )

    schema = _load_signature_schema(schema_path=schema_path)

    with open(input_path, "rb") as f:
        raw_bytes = f.read()

    file_type: C2PA_ContentTypes = _get_content_type_by_filepath(file_path=input_path)

    if file_type.name == "pdf":
        cai_offset = len(raw_bytes)
    else:
        cai_offset = 2

    creative_work_assertion = c2pie_GenerateAssertion(
        C2PA_AssertionTypes.creative_work,
        schema,
    )

    hash_data_assertion = c2pie_GenerateHashDataAssertion(
        cai_offset=cai_offset, hashed_data=hashlib.sha256(raw_bytes).digest()
    )

    assertions = [creative_work_assertion, hash_data_assertion]

    manifest = c2pie_GenerateManifest(
        assertions=assertions,
        private_key=key,
        certificate_chain=certificates,
    )

    signed_bytes = c2pie_EmplaceManifest(
        format_type=file_type,
        content_bytes=raw_bytes,
        c2pa_offset=cai_offset,
        manifests=manifest,
    )

    with open(output_path, "wb") as output_file:
        output_file.write(signed_bytes)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")
