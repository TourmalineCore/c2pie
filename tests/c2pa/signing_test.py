from c2pie.signing import _generate_hashed_uri_map


def test_generate_hashed_uri_map_required_fields():
    result = _generate_hashed_uri_map(url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3", hash_value=b"\x01\x02\x03")
    assert result["url"] == "self#jumbf=c2pa.assertions/c2pa.ingredient.v3"
    assert result["hash"] == b"\x01\x02\x03"


def test_generate_hashed_uri_map_no_alg_by_default():
    result = _generate_hashed_uri_map(url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3", hash_value=b"\x01\x02\x03")
    assert "alg" not in result


def test_generate_hashed_uri_map_with_alg():
    result = _generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
        hash_algorithm="sha256",
    )
    assert result["alg"] == "sha256"
