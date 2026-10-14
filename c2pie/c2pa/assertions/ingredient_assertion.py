import hashlib
import io
from typing import Any

import c2pa

from c2pie.c2pa.assertions.base_assertion import Assertion
from c2pie.c2pa.assertions.ingredient_thumbnail_assertion import IngredientThumbnailAssertion
from c2pie.c2pa_parsing.jumbf_parsing import find_in_box
from c2pie.jumbf_boxes.box import Box
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes
from c2pie.utils.generate_hashed_uri_map import generate_hashed_uri_map


class IngredientAssertion(Assertion):
    """c2pa.ingredient.v3 asset-binding assertion."""

    def __init__(
        self,
        title: str,
        dc_format: str,
        ingredient_bytes: bytes,
        active_manifest_urn: str | None,
        active_manifest: Box | None,
        ingredient_thumbnail_assertion: IngredientThumbnailAssertion | None = None,
    ):
        self.schema: dict[str, Any] = {
            # Optional (per CDDL: "? dc:title"). Human-readable name of the
            # ingredient, e.g. the original filename or asset title.
            "dc:title": title,
            # Optional (per CDDL: "? dc:format"). Media Type (MIME type) of
            # the ingredient, e.g. "image/jpeg" or "application/pdf".
            "dc:format": dc_format,
            # Required. Describes the relationship of this ingredient to the
            # asset it is an ingredient of. Per spec Table 10, valid values:
            # "parentOf"    - the current asset is a derived/rendered version
            #                 of this ingredient (at most one parent per manifest);
            # "componentOf" - the current asset is composed of multiple parts,
            #                 this ingredient being one of them;
            # "inputTo"     - this ingredient was used as input to a
            #                 computational process (e.g. AI/ML model) that
            #                 led to the creation/modification of this asset.
            "relationship": "parentOf",
        }

        if ingredient_thumbnail_assertion:
            ingredient_thumbnail_hash = hashlib.sha256(ingredient_thumbnail_assertion.payload).digest()

            ingredient_thumbnail: dict[str, str | bytes] = generate_hashed_uri_map(
                url=f"self#jumbf=c2pa.assertions/{ingredient_thumbnail_assertion.get_label()}",
                hash_value=ingredient_thumbnail_hash,
                hash_algorithm="sha256",
            )
            self.schema["thumbnail"] = ingredient_thumbnail

        if active_manifest_urn and active_manifest:
            validation_results = self.validate_ingredient(
                ingredient_bytes,
                dc_format,
            )

            # We should not include information about the active manifest if validation was unsuccessful
            if not validation_results:
                content_boxes = self.content_box_from_schema(C2PA_AssertionTypes.ingredient, self.schema)

                super().__init__(
                    C2PA_AssertionTypes.ingredient,
                    content_boxes,
                )
                return

            active_manifest_hash = hashlib.sha256(active_manifest.payload).digest()

            active_manifest_map: dict[str, str | bytes] = generate_hashed_uri_map(
                url=f"self#jumbf=/c2pa/{active_manifest_urn}",
                hash_value=active_manifest_hash,
                hash_algorithm="sha256",
            )

            claim_signature_box = find_in_box(active_manifest, "c2pa.signature")

            claim_signature_hash = hashlib.sha256(claim_signature_box.payload).digest()

            claim_signature: dict[str, str | bytes] = generate_hashed_uri_map(
                url=f"self#jumbf=/c2pa/{active_manifest_urn}/c2pa.signature",
                hash_value=claim_signature_hash,
                hash_algorithm="sha256",
            )

            self.schema["activeManifest"] = active_manifest_map
            self.schema["validationResults"] = validation_results
            self.schema["claimSignature"] = claim_signature

        content_boxes = self.content_box_from_schema(C2PA_AssertionTypes.ingredient, self.schema)

        super().__init__(C2PA_AssertionTypes.ingredient, content_boxes)

    def validate_ingredient(
        self,
        ingredient_bytes: bytes,
        mime_type: str,
    ) -> dict | None:
        stream = io.BytesIO(ingredient_bytes)
        # Reader.try_create is a factory method that attempts to create a Reader
        # for the given stream/mime type. Returns a Reader instance if a C2PA
        # manifest (JUMBF data) is found in the asset, or None if no manifest
        # is present (instead of raising ManifestNotFound).
        # Raises an exception for any other error unrelated to a missing manifest.
        c2pa_instance = c2pa.Reader.try_create(mime_type, stream)

        if not c2pa_instance:
            return None

        with c2pa_instance:
            return c2pa_instance.get_validation_results()
