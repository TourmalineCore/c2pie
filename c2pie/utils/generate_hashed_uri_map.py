def generate_hashed_uri_map(
    url: str,
    hash_value: bytes,
    hash_algorithm: str | None = None,
) -> dict[str, str | bytes]:
    schema: dict[str, str | bytes] = {
        "url": url,
        "hash": hash_value,
    }

    if hash_algorithm:
        schema["alg"] = hash_algorithm

    return schema