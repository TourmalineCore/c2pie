from c2pie.c2pa.manifest import Manifest
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.jumbf_boxes.box import Box
from c2pie.utils.content_types import c2pa_content_types


def test_create_manifest_store_witn_no_content():
    test_manifest_store = ManifestStore()

    assert test_manifest_store is not None
    assert test_manifest_store.get_content_type() == c2pa_content_types["manifest_store"]
    assert test_manifest_store.get_label() == "c2pa"
    assert len(test_manifest_store.manifests) == 0
    assert len(test_manifest_store.content_boxes) == 0


def test_create_manifest_store_with_manifests():
    test_manifests = [Manifest(), Manifest()]

    test_manifest_store = ManifestStore(manifests=test_manifests)

    assert len(test_manifest_store.manifests) != 0
    assert len(test_manifest_store.content_boxes) != 0


def _prior_manifest_bytes(label: str) -> bytes:
    return Manifest(manifest_label=label).serialize()


def test_manifest_store_with_prior_manifests_content_boxes_count():
    prior = [_prior_manifest_bytes("urn:c2pa:old1"), _prior_manifest_bytes("urn:c2pa:old2")]
    new_manifest = Manifest(manifest_label="urn:c2pa:new")
    store = ManifestStore([*prior, new_manifest])
    # 2 prior boxes + 1 new manifest
    assert len(store.content_boxes) == 3


def test_manifest_store_with_prior_manifests_new_manifest_last():
    prior = [_prior_manifest_bytes("urn:c2pa:old")]
    new_manifest = Manifest(manifest_label="urn:c2pa:new")
    store = ManifestStore([*prior, new_manifest])
    assert store.content_boxes[-1] is new_manifest


def test_manifest_store_without_prior_manifests_unaffected():
    new_manifest = Manifest(manifest_label="urn:c2pa:only")
    store = ManifestStore([new_manifest])
    assert len(store.content_boxes) == 1


def test_manifest_store_only_manifest_objects_tracked_in_manifests():
    prior = _prior_manifest_bytes("urn:c2pa:old")
    new_manifest = Manifest(manifest_label="urn:c2pa:new")
    store = ManifestStore([prior, new_manifest])
    assert store.manifests == [new_manifest]


def test_manifest_store_with_prior_manifests_serializes_without_error():
    prior = _prior_manifest_bytes("urn:c2pa:prior")
    store = ManifestStore([prior, Manifest()])
    result = store.serialize()
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_manifest_store_set_hash_data_length_only_affects_new_manifests():
    prior_bytes = _prior_manifest_bytes("urn:c2pa:prior")

    new_manifest = Manifest(manifest_label="urn:c2pa:new")
    store = ManifestStore([prior_bytes, new_manifest])
    # set_hash_data_length_for_all should not raise, prior boxes are not touched
    store.set_hash_data_length_for_all(1024)

    # Prior manifest raw bytes are unchanged (they're stored as parsed Box objects)
    prior_box = store.content_boxes[0]
    assert prior_box.serialize() == prior_bytes


def test_manifest_store_empty_list_equivalent_to_no_args():
    store = ManifestStore([])
    assert len(store.manifests) == 0
    assert len(store.content_boxes) == 0
