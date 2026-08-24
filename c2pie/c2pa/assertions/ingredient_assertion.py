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
        schema: dict[str, Any] = {
            "dc:title": title,
            "dc:format": dc_format,
            "relationship": "parentOf",
        }

        if ingredient_thumbnail_assertion:
            ingredient_thumbnail_hash = hashlib.sha256(ingredient_thumbnail_assertion.payload).digest()

            ingredient_thumbnail: dict[str, str | bytes] = generate_hashed_uri_map(
                url=f"self#jumbf=c2pa.assertions/{ingredient_thumbnail_assertion.get_label()}",
                hash_value=ingredient_thumbnail_hash,
                hash_algorithm="sha256",
            )
            schema["thumbnail"] = ingredient_thumbnail

        if active_manifest_urn and active_manifest:
            validation_results = self.validate_ingredient(
                ingredient_bytes,
                dc_format,
            )

            # We should not include information about the active manifest if validation was unsuccessful
            if not validation_results:
                super().__init__(
                    C2PA_AssertionTypes.ingredient,
                    schema,
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

            schema["activeManifest"] = active_manifest_map
            schema["validationResults"] = validation_results
            schema["claimSignature"] = claim_signature

        super().__init__(
            C2PA_AssertionTypes.ingredient,
            schema,
        )

    def validate_ingredient(
        self,
        ingredient_bytes: bytes,
        mime_type: str,
    ) -> dict | None:
        stream = io.BytesIO(ingredient_bytes)
        reader = c2pa.Reader.try_create(mime_type, stream)

        if not reader:
            return None

        with reader:
            return reader.get_validation_results()
