from __future__ import annotations

import hashlib
import uuid
from typing import Any

import cbor2

from tc_c2pa_py.jumbf_boxes.content_box import ContentBox
from tc_c2pa_py.jumbf_boxes.super_box import SuperBox
from tc_c2pa_py.utils.content_types import c2pa_content_types


def _sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


class Claim(SuperBox):
    """
    Claim (c2pa.claim) как JUMBF superbox с одним CBOR content box.

    Совместимость с тестами:
      - есть поле `claim_signature_label` ровно в формате:
        'self#jumbf=c2pa/<manifest_label>/c2pa.signature'  (без ведущего '/')
    В бою (для c2patool) мы кладём hashed-URI assertion'ов в виде:
        'self#jumbf=/c2pa/<manifest_label>/c2pa.assertions/<assertion-label>'
    """

    def __init__(
        self,
        claim_generator: str = "tc_c2pa_py",
        manifest_label: str | None = None,
        assertion_store=None,
        dc_format: str | None = None,
    ):
        self.claim_generator = claim_generator
        self.manifest_label = manifest_label or f"urn:c2pa:{uuid.uuid4().hex}"
        self.assertion_store = assertion_store
        self.dc_format = dc_format

        self.claim_signature_label = f"self#jumbf=c2pa/{self.manifest_label}/c2pa.signature"

        self._instance_id = f"xmp:iid:{uuid.uuid4()}"

        cbor_payload = self._build_cbor_payload()

        content_box = ContentBox(
            box_type=b"cbor".hex(),
            payload=cbor_payload,
        )
        super().__init__(
            content_type=c2pa_content_types["claim"],
            label="c2pa.claim",
            content_boxes=[content_box],
        )

    def get_cbor_payload(self) -> bytes:
        """Байты CBOR, поверх которых подписывается COSE (detached)."""
        return self.content_boxes[0].get_payload()

    def get_manifest_label(self) -> str:
        return self.manifest_label

    def set_assertion_store(self, assertion_store) -> None:
        """
        Вызывается из Manifest при изменении assertion'ов (в т.ч. когда обновили length в c2pa.hash.data).
        Пересобираем CBOR payload клейма с корректными hashed-URI.
        """
        self.assertion_store = assertion_store
        self._rebuild_payload()

    def set_format(self, dc_format: str | None) -> None:
        self.dc_format = dc_format
        self._rebuild_payload()

    def _build_assertions_array(self) -> list[dict[str, Any]]:
        """
        Строим массив claim['assertions'] из текущего AssertionStore:
          - url:  self#jumbf=/c2pa/<manifest_label>/c2pa.assertions/<label>
          - alg:  sha256
          - hash: sha256( JUMBF-superbox-content = description + content_boxes ) для этого assertion
        """
        out: list[dict[str, Any]] = []
        if not self.assertion_store:
            return out

        assertions = getattr(self.assertion_store, "assertions", None)
        if assertions is None and hasattr(self.assertion_store, "get_assertions"):
            assertions = self.assertion_store.get_assertions()
        if not assertions:
            return out

        for a in assertions:
            label = getattr(a, "label", None)
            if label is None and hasattr(a, "get_label"):
                label = a.get_label()

            if hasattr(a, "get_data_for_signing"):
                data = a.get_data_for_signing()
            else:
                data = a.description_box.serialize() + a.serialize_content_boxes()

            out.append(
                {
                    "url": f"self#jumbf=/c2pa/{self.manifest_label}/c2pa.assertions/{label}",
                    "alg": "sha256",
                    "hash": _sha256(data),
                }
            )
        return out

    def _build_cbor_payload(self) -> bytes:
        """
        Каноничный CBOR-контент claim.
        Включаем:
          - claim_generator
          - instanceID (стабилен для объекта)
          - signature (ссылка на c2pa.signature)
          - опционально dc:format
          - опционально assertions (если есть assertion_store)
        """
        m: dict[str, Any] = {
            "claim_generator": self.claim_generator,
            "instanceID": self._instance_id,
            "signature": self.claim_signature_label,
            "alg": "sha256",
        }
        if self.dc_format:
            m["dc:format"] = self.dc_format

        assertions_arr = self._build_assertions_array()
        if assertions_arr:
            m["assertions"] = assertions_arr

        return cbor2.dumps(m, canonical=True)

    def _rebuild_payload(self) -> None:
        new_payload = self._build_cbor_payload()
        self.content_boxes[0] = ContentBox(
            box_type=b"cbor".hex(),
            payload=new_payload,
        )
        self.sync_payload()
