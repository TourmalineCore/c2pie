import hashlib
import os
from enum import Enum

from c2pie.interface import (
    C2PA_AssertionTypes,
    TC_C2PA_EmplaceManifest,
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
)

creative_work_schema = {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "author": [{"@type": "Person", "name": "Tourmaline Core"}],
    "copyrightYear": "2026",
    "copyrightHolder": "c2pie",
}


def _load_certificates_and_key(
    key_path: str,
    certificates_path: str,
) -> list[bytes]:
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
    file_type: Enum,
    input_path: str,
    output_path: str,
    key_path: str | None = os.getenv("C2PIE_KEY_FILEPATH"),
    certificates_path: str | None = os.getenv("C2PIE_CERT_FILEPATH"),
) -> None:
    with open(input_path, "rb") as f:
        raw_bytes = f.read()

    key, certificates = _load_certificates_and_key(
        key_path=key_path,
        certificates_path=certificates_path,
    )

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

    manifest = TC_C2PA_GenerateManifest(assertions=assertions, private_key=key, certificate_chain=certificates)

    signed_bytes = TC_C2PA_EmplaceManifest(
        format_type=file_type,
        content_bytes=raw_bytes,
        c2pa_offset=cai_offset,
        manifests=manifest,
    )

    with open(output_path, "wb") as output_file:
        output_file.write(signed_bytes)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")
