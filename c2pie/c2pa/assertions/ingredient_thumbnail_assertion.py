from c2pie.c2pa.assertions.embedded_data_assertion import EmbeddedDataAssertion
from c2pie.utils.assertion_schemas import C2PA_AssertionTypes


class IngredientThumbnailAssertion(EmbeddedDataAssertion):
    """An assertion (c2pa.thumbnail.ingredient) containing an ingredient thumbnail"""

    def __init__(
        self,
        media_type: str,
        image_data: bytes,
    ):
        super().__init__(
            media_type=media_type,
            image_data=image_data,
            assertion_type=C2PA_AssertionTypes.ingredient_thumbnail,
        )
