from __future__ import annotations
from typing import Optional, List

from tc_c2pa_py.jumbf_boxes.super_box import SuperBox
from tc_c2pa_py.utils.content_types import c2pa_content_types


class ManifestStore(SuperBox):
    """
    C2PA Manifest Store (JUMBF superbox) с одним или несколькими Manifest.
    ВАЖНО: здесь мы НЕ «угадываем» транспортные накладные байты (JPEG/PDF и т.п.).
    Для PDF длину исключения выставляет инжектор; для JPEG — свой инжектор.
    """

    def __init__(self, manifests: Optional[list] = None):
        self.manifests: List = [] if manifests is None else manifests
        super().__init__(content_type=c2pa_content_types['manifest_store'],
                         label='c2pa',
                         content_boxes=self.manifests)

    def sync_payload(self):
        super().sync_payload()

    def set_hash_data_length_for_all(self, length: int) -> None:
        for m in self.manifests:
            m.set_hash_data_length(length)
        super().sync_payload()

    def serialize(self) -> bytes:
        return super().serialize()
