from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any

import cbor2

from c2pie.c2pa.assertion_store import AssertionStore
from c2pie.jumbf_boxes.content_box import ContentBox
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types

_GATHERED_ASSERTIONS = {"c2pa.ingredient.v3", "c2pa.actions.v2"}


def _sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


class Claim(SuperBox):
    """Claim (c2pa.claim.v2) as a JUMBF superbox with one CBOR content box."""

    def __init__(
        self,
        assertion_store: AssertionStore,
        manifest_label: str,
        dc_title: Path,
    ):
        self.manifest_label = manifest_label
        self.assertion_store = assertion_store
        self.dc_title = dc_title

        self.claim_signature_label = f"self#jumbf=c2pa/{self.manifest_label}/c2pa.signature"
        self.instance_id = f"xmp:iid:{uuid.uuid4()}"

        cbor_payload = self._build_cbor_payload()

        content_box = ContentBox(
            box_type=b"cbor".hex(),
            payload=cbor_payload,
        )

        super().__init__(
            content_type=c2pa_content_types["claim"],
            label="c2pa.claim.v2",
            content_boxes=[content_box],
        )

    def get_cbor_payload(self) -> bytes:
        """CBOR bytes, on top of which COSE (detached) is signed."""
        return self.content_boxes[0].get_payload()

    def get_manifest_label(self) -> str:
        return self.manifest_label

    def set_assertion_store(self, assertion_store) -> None:
        """
        Called from Manifest when assertions are changed (including when length is updated in c2pa.hash.data).
        Reassemble the CBOR payload of the stamp with the correct hashed URIs.
        """
        self.assertion_store = assertion_store
        self._rebuild_payload()

    def _build_assertions_array(self) -> list[dict[str, Any]]:
        """
        Build the claim["created_assertions"] and claim["gathered_assertions"] arrays from the current AssertionStore:
          - url:  self#jumbf=/c2pa/<manifest_label>/c2pa.assertions/<label>
          - alg:  sha256
          - hash: sha256( JUMBF-superbox-content = description + content_boxes ) for this assertion
        """
        created_assertions: list[dict[str, Any]] = []
        gathered_assertions: list[dict[str, Any]] = []

        if not self.assertion_store:
            return created_assertions, gathered_assertions

        assertions = getattr(self.assertion_store, "assertions", None)
        if assertions is None and hasattr(self.assertion_store, "get_assertions"):
            assertions = self.assertion_store.get_assertions()

        if not assertions:
            return created_assertions, gathered_assertions

        for assertion in assertions:
            label = getattr(assertion, "label", None)
            if label is None and hasattr(assertion, "get_label"):
                label = assertion.get_label()

            if hasattr(assertion, "get_data_for_signing"):
                data = assertion.get_data_for_signing()
            else:
                data = assertion.description_box.serialize() + assertion.serialize_content_boxes()

            if label in _GATHERED_ASSERTIONS:
                gathered_assertions.append(
                    {
                        "url": f"self#jumbf=/c2pa/{self.manifest_label}/c2pa.assertions/{label}",
                        "alg": "sha256",
                        "hash": _sha256(data),
                    }
                )
            else:
                created_assertions.append(
                    {
                        "url": f"self#jumbf=/c2pa/{self.manifest_label}/c2pa.assertions/{label}",
                        "alg": "sha256",
                        "hash": _sha256(data),
                    }
                )

        return created_assertions, gathered_assertions

    def _build_cbor_payload(self) -> bytes:
        """
        Canonical CBOR content claim.
        Include:
          - claim_generator_info
          - instanceID (stable for the object)
          - signature (reference to c2pa.signature)
          - optional created_assertions (if there is an assertion_store)
          - optional gathered_assertions (if there is an assertion_store)
          - optional dc:title
        """
        claim: dict[str, Any] = {
            "claim_generator_info": {
                "name": "c2pie",
                "specVersion": "2.4.0",
            },
            "instanceID": self.instance_id,
            "signature": self.claim_signature_label,
            "dc:title": self.dc_title,
            "alg": "sha256",
        }

        created_assertions, gathered_assertions = self._build_assertions_array()

        if created_assertions:
            claim["created_assertions"] = created_assertions

        if gathered_assertions:
            claim["gathered_assertions"] = gathered_assertions

        return cbor2.dumps(claim, canonical=True)

    def _rebuild_payload(self) -> None:
        new_payload = self._build_cbor_payload()
        self.content_boxes[0] = ContentBox(
            box_type=b"cbor".hex(),
            payload=new_payload,
        )

        self.sync_payload()
