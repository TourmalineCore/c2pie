import uuid

from tc_c2pa_py.jumbf_boxes.super_box import SuperBox
from tc_c2pa_py.utils.content_types import c2pa_content_types


class Manifest(SuperBox):
    """
    Один C2PA Manifest: Assertion Store + Claim + Claim Signature.
    Лейбл манифеста совместим со c2patool: urn:c2pa:<uuid-hex>
    """

    def __init__(self, claim=None, claim_signature=None, assertion_store=None):
        self.claim = claim
        self.claim_signature = claim_signature
        self.assertion_store = assertion_store
        self.manifest_label = f"urn:c2pa:{uuid.uuid4().hex}"

        super().__init__(content_type=c2pa_content_types["default_manifest"], label=self.manifest_label)

    def set_claim(self, claim):
        self.claim = claim
        self.add_content_box(self.claim)

    def set_claim_signature(self, claim_signature):
        self.claim_signature = claim_signature
        self.add_content_box(self.claim_signature)

    def set_assertion_store(self, assertion_store):
        self.assertion_store = assertion_store
        self.add_content_box(self.assertion_store)

    def get_manifest_label(self):
        return self.manifest_label

    def get_assertions(self):
        return self.assertion_store.get_assertions()

    def set_hash_data_length(self, length: int):
        """
        Обновляет длину исключений в HashData, пересобирает Claim (хэши assertion-ов)
        и ClaimSignature (COSE Sign1 detatched over Claim CBOR).
        """
        self.assertion_store.set_hash_data_length(length)

        self.claim.set_assertion_store(self.assertion_store)

        self.claim_signature.set_claim(self.claim)

        self.sync_payload()
