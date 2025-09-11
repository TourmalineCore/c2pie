import hashlib

from c2pie.interface import (
    C2PA_AssertionTypes,
    C2PA_ContentTypes,
    TC_C2PA_EmplaceManifest,
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
)


def sign_image(
    input_path: str = "tests/fixtures/test_image.jpg",
    output_path: str = "test_application/test_injected_image.jpg",
) -> None:
    key_filepath = "tests/fixtures/crypto/ps256.pem"
    cert_filepath = "tests/fixtures/crypto/ps256.pub"

    if key_filepath != "":
        with open(key_filepath, "rb") as f:
            key = f.read()
    else:
        key = []

    if cert_filepath != "":
        with open(cert_filepath, "rb") as f:
            certificate = f.read()
    else:
        key = []

    cai_offset = 2

    with open(input_path, "rb") as binary_image:
        raw_bytes = binary_image.read()

    creative_work_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "author": [{"@type": "Person", "name": "Tourmaline Core"}],
        "copyrightYear": "2024",
        "copyrightHolder": "tc-c2pa-py",
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


if __name__ == "__main__":
    sign_image()
