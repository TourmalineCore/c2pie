from __future__ import annotations

from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


class ManifestStore(SuperBox):
    """
    C2PA Manifest Store (JUMBF superbox) with one or more Manifest.
    IMPORTANT: here we do NOT "assume" length of specific manifest bytes (JPG/PDF, etc.).
    For PDF, the length of the exception is set by the injector; for JPG, by its own injector.
    """

    def __init__(self, manifests: list | None = None):
        self.manifests: list[Manifest] = [] if manifests is None else manifests

        super().__init__(
            content_type=c2pa_content_types["manifest_store"],
            label="c2pa",
            content_boxes=self.manifests,
        )

    def sync_payload(self):
        super().sync_payload()

    def set_hash_data_length_for_all(
        self,
        length: int,
    ) -> None:
        self.manifests[-1].set_hash_data_length(length)

        super().sync_payload()

    def serialize(self) -> bytes:
        return super().serialize()
