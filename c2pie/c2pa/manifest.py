import uuid

from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


class Manifest(SuperBox):
    """
    C2PA Manifest: Assertion Store + Claim + Claim Signature.
    The manifest label is compatible with c2patool: urn:c2pa:<uuid-hex>
    """

    def __init__(
        self,
        manifest_label: str = f"urn:c2pa:{uuid.uuid4().hex}",
    ):
        self.manifest_label = manifest_label
        self.claim = None
        self.claim_signature = None
        self.assertion_store = None

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
        if self.assertion_store:
            return self.assertion_store.get_assertions()
        return

    def set_hash_data_length(self, length: int):
        """
        Updates the length of exceptions in HashData, reassembles Claim (assertion hashes)
        and ClaimSignature (COSE Sign1 detached over Claim CBOR).
        """
        if self.assertion_store and self.claim and self.claim_signature:
            self.assertion_store.set_hash_data_length(length)

            self.claim.set_assertion_store(self.assertion_store)

            self.claim_signature.set_claim(self.claim)

        self.sync_payload()
