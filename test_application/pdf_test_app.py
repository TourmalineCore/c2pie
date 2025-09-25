import hashlib

from c2pie.interface import (
    C2PA_AssertionTypes,
    C2PA_ContentTypes,
    TC_C2PA_EmplaceManifest,
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
)


def sign_pdf(
    input_path: str = "tests/fixtures/test_doc.pdf",
    output_path: str = "test_application/test_injected_document.pdf",
) -> None:
    key_filepath = "tests/fixtures/crypto/ps256.pem"
    cert_filepath = "tests/fixtures/crypto/ps256.pub"

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
        "copyrightHolder": "tc-c2pa-py",
    }
    creative_work_assertion = TC_C2PA_GenerateAssertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

    hash_data_assertion = TC_C2PA_GenerateHashDataAssertion(
        cai_offset=cai_offset, hashed_data=hashlib.sha256(raw_pdf).digest()
    )

    assertions = [creative_work_assertion, hash_data_assertion]

    manifest = TC_C2PA_GenerateManifest(assertions=assertions, private_key=key, certificate_chain=certificate)

    result_pdf = TC_C2PA_EmplaceManifest(C2PA_ContentTypes.pdf, raw_pdf, cai_offset, manifest)

    with open(output_path, "wb") as f:
        f.write(result_pdf)


if __name__ == "__main__":
    sign_pdf()
