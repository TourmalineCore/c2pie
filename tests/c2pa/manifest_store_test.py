from c2pie.c2pa.manifest import Manifest
from c2pie.c2pa.manifest_store import ManifestStore
from c2pie.utils.content_types import c2pa_content_types


def _previous_manifest_to_bytes(manifest_label: str) -> bytes:
    return Manifest(manifest_label=manifest_label).serialize()


def test_create_manifest_store_witn_no_content():
    test_manifest_store = ManifestStore()
    assert test_manifest_store is not None
    assert test_manifest_store.get_content_type() == c2pa_content_types["manifest_store"]
    assert test_manifest_store.get_label() == "c2pa"
    assert len(test_manifest_store.manifests) == 0
    assert len(test_manifest_store.content_boxes) == 0


def test_create_manifest_store_with_manifest():
    manifest_store = ManifestStore(manifests=[Manifest()])
    assert len(manifest_store.manifests) == 1
    assert len(manifest_store.content_boxes) == 1


def test_manifest_store_with_previous_manifests_content_boxes_count():
    previous_manifests = [
        _previous_manifest_to_bytes("urn:c2pa:previous-manifest1"),
        _previous_manifest_to_bytes("urn:c2pa:previous-manifest2"),
    ]

    manifest = Manifest(manifest_label="urn:c2pa:new-manifest")

    manifest_store = ManifestStore(
        [
            *previous_manifests,
            manifest,
        ],
    )

    assert len(manifest_store.manifests) == 3
    assert len(manifest_store.content_boxes) == 3


def test_manifest_store_with_previous_manifests_new_manifest_last():
    previous_manifests = [
        _previous_manifest_to_bytes("urn:c2pa:previous-manifest"),
    ]

    manifest = Manifest(manifest_label="urn:c2pa:new-manifest")

    manifest_store = ManifestStore(
        [
            *previous_manifests,
            manifest,
        ],
    )

    assert manifest_store.content_boxes[-1] is manifest


def test_manifest_store_with_previous_manifests_serializes_without_error():
    previous_manifest = _previous_manifest_to_bytes("urn:c2pa:previous-manifest")
    manifest_store = ManifestStore([previous_manifest, Manifest()])
    manifest_store_bytes = manifest_store.serialize()
    assert isinstance(manifest_store_bytes, bytes)
    assert len(manifest_store_bytes) > 0


def test_manifest_store_set_hash_data_length_only_affects_new_manifests():
    previous_manifest = _previous_manifest_to_bytes("urn:c2pa:previous-manifest")
    new_manifest = Manifest(manifest_label="urn:c2pa:new-manifest")
    manifest_store = ManifestStore([previous_manifest, new_manifest])
    manifest_store.set_hash_data_length_for_all(1024)
    previous_box = manifest_store.content_boxes[0]
    assert previous_box.serialize() == previous_manifest


def test_manifest_store_empty_list_equivalent_to_no_args():
    manifest_store = ManifestStore([])
    assert len(manifest_store.manifests) == 0
    assert len(manifest_store.content_boxes) == 0
