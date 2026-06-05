from c2pie.c2pa.manifest import Manifest
from c2pie.jumbf_boxes.super_box import SuperBox
from c2pie.utils.content_types import c2pa_content_types


class ManifestStore(SuperBox):
    """
    C2PA Manifest Store (JUMBF superbox) with one or more Manifest.
    IMPORTANT: here we do NOT "assume" length of specific manifest bytes (JPG/PDF, etc.).
    For PDF, the length of the exception is set by the injector; for JPG, by its own injector.
    """

    def __init__(
        self,
        manifests: list[Manifest] | None = None,
    ):
        self.manifests: list[Manifest] = [] if manifests is None else manifests

        super().__init__(
            content_type=c2pa_content_types["manifest_store"],
            label="c2pa",
            content_boxes=self.manifests,
        )

    def sync_payload(self):
        super().sync_payload()

    def add_full_c2pa_structure_exclusion(
        self,
        offset: int,
        length: int,
    ) -> None:
        self.manifests[-1].add_full_c2pa_structure_exclusion(
            offset,
            length,
        )

        super().sync_payload()

    def serialize(self) -> bytes:
        if self.l_box > 0xFFFFFFFF:
            raise ValueError(
                f"Manifest Store is too large to serialize: {self.l_box:,} bytes. "
                "The JUMBF LBox field is limited to 4 bytes (max 4,294,967,295 bytes)."
            )

        return super().serialize()
