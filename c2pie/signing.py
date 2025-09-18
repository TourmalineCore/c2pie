import hashlib
import os

from c2pie.interface import (
    C2PA_AssertionTypes,
    C2PA_ContentTypes,
    TC_C2PA_EmplaceManifest,
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
)

# TODO: move common functionality to separate functions and reuse them


def sign_pdf(
    key_filepath: str | None = os.getenv("C2PIE_KEY_FILEPATH"),
    cert_filepath: str | None = os.getenv("C2PIE_CERT_FILEPATH"),
    input_path: str = "tests/fixtures/test_doc.pdf",
    output_path: str | None = None,
) -> None:
    if not key_filepath:
        print("Key filepath variable has not been set. Cannot sign the provided file.")
        return
    if not cert_filepath:
        print("Cert filepath variable has not been set. Cannot sign the provided file.")
        return

    if not output_path:
        directory, filename = os.path.split(input_path)[0], os.path.split(input_path)[1]
        output_path = directory + "/signed_" + filename

    with open(key_filepath, "rb") as f:
        key = f.read()
    with open(cert_filepath, "rb") as f:
        certificate = f.read()

    with open(input_path, "rb") as f:
        raw_pdf = f.read()

    cai_offset = len(raw_pdf)

    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }
    creative_work_assertion = TC_C2PA_GenerateAssertion(
        C2PA_AssertionTypes.creative_work,
        creative_work_schema,
    )

    hash_data_assertion = TC_C2PA_GenerateHashDataAssertion(
        cai_offset=cai_offset, hashed_data=hashlib.sha256(raw_pdf).digest()
    )

    assertions = [creative_work_assertion, hash_data_assertion]

    manifest = TC_C2PA_GenerateManifest(assertions=assertions, private_key=key, certificate_chain=certificate)

    result_pdf = TC_C2PA_EmplaceManifest(
        format_type=C2PA_ContentTypes.pdf,
        content_bytes=raw_pdf,
        c2pa_offset=cai_offset,
        manifests=manifest,
    )

    with open(output_path, "wb") as f:
        f.write(result_pdf)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")


def sign_image(
    key_filepath: str | None = os.getenv("C2PIE_KEY_FILEPATH"),
    cert_filepath: str | None = os.getenv("C2PIE_CERT_FILEPATH"),
    input_path: str = "tests/fixtures/test_image.jpg",
    output_path: str | None = None,
) -> None:
    if not key_filepath:
        print("Key filepath variable has not been set. Cannot sign the provided image.")
        return
    if not cert_filepath:
        print("Cert filepath variable has not been set. Cannot sign the provided image.")
        return

    if not output_path:
        directory, filename = os.path.split(input_path)[0], os.path.split(input_path)[1]
        output_path = directory + "/signed_" + filename

    with open(key_filepath, "rb") as f:
        key = f.read()

    with open(cert_filepath, "rb") as f:
        certificate = f.read()

    with open(input_path, "rb") as binary_image:
        raw_bytes = binary_image.read()

    cai_offset = 2

    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "c2pie",
    }
    creative_work_assertion = TC_C2PA_GenerateAssertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

    hash_data_assertion = TC_C2PA_GenerateHashDataAssertion(
        cai_offset=cai_offset, hashed_data=hashlib.sha256(raw_bytes).digest()
    )

    assertions = [creative_work_assertion, hash_data_assertion]

    manifest = TC_C2PA_GenerateManifest(assertions=assertions, private_key=key, certificate_chain=certificate)

    raw_bytes = TC_C2PA_EmplaceManifest(C2PA_ContentTypes.jpg, raw_bytes, cai_offset, manifest)

    with open(output_path, "wb") as binary_file:
        binary_file.write(raw_bytes)

    print(f"Successfully signed the file {input_path}!\nThe result was saved to {output_path}.")
