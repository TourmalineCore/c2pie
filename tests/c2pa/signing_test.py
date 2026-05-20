from c2pie.utils.generate_hashed_uri_map import generate_hashed_uri_map


def test_generate_hashed_uri_map_required_fields():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
    )
    assert hash_uri_map["url"] == "self#jumbf=c2pa.assertions/c2pa.ingredient.v3"
    assert hash_uri_map["hash"] == b"\x01\x02\x03"


def test_generate_hashed_uri_map_no_alg_by_default():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
    )
    assert "alg" not in hash_uri_map


def test_generate_hashed_uri_map_with_alg():
    hash_uri_map = generate_hashed_uri_map(
        url="self#jumbf=c2pa.assertions/c2pa.ingredient.v3",
        hash_value=b"\x01\x02\x03",
        hash_algorithm="sha256",
    )
    assert hash_uri_map["alg"] == "sha256"
