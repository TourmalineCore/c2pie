import hashlib

from tc_c2pa_py.interface import (
    TC_C2PA_GenerateAssertion,
    TC_C2PA_GenerateHashDataAssertion,
    TC_C2PA_GenerateManifest,
    TC_C2PA_EmplaceManifest,
    C2PA_ContentTypes,
    C2PA_AssertionTypes,
)

key_filepath = 'tests/fixtures/crypto/ps256.pem'   
cert_filepath = 'tests/fixtures/crypto/ps256.pub'  

with open(key_filepath, 'rb') as f:
    key = f.read()
with open(cert_filepath, 'rb') as f:
    certificate = f.read()

src_pdf = "tests/fixtures/test_doc.pdf"
dst_pdf = "test_application/test_injected_document.pdf"

with open(src_pdf, "rb") as f:
    raw_pdf = f.read()

cai_offset = len(raw_pdf)

creative_work_schema = {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "author": [{"@type": "Person", "name": "Tourmaline Core"}],
    "copyrightYear": "2024",
    "copyrightHolder": "tc-c2pa-py"
}
creative_work_assertion = TC_C2PA_GenerateAssertion(C2PA_AssertionTypes.creative_work, creative_work_schema)

hash_data_assertion = TC_C2PA_GenerateHashDataAssertion(
    cai_offset=cai_offset,
    hashed_data=hashlib.sha256(raw_pdf).digest()
)

assertions = [creative_work_assertion, hash_data_assertion]

manifest = TC_C2PA_GenerateManifest(
    assertions=assertions,
    private_key=key,
    certificate_chain=certificate
)

result_pdf = TC_C2PA_EmplaceManifest(C2PA_ContentTypes.pdf, raw_pdf, cai_offset, manifest)

with open(dst_pdf, "wb") as f:
    f.write(result_pdf)

print(f"[PDF] Wrote: {dst_pdf}")
