from tc_c2pa_py.c2pa.manifest import Manifest
from tc_c2pa_py.c2pa.manifest_store import ManifestStore
from tc_c2pa_py.utils.content_types import c2pa_content_types


def test_create_manifest_store():
    test_manifest_store = ManifestStore()

    assert test_manifest_store is not None
    assert test_manifest_store.get_content_type() == c2pa_content_types["manifest_store"]
    assert test_manifest_store.get_label() == "c2pa"
    assert len(test_manifest_store.manifests) == 0
    assert len(test_manifest_store.content_boxes) == 0


def test_create_manifest_store_with_content():
    test_manifests = [Manifest(), Manifest()]

    test_manifest_store = ManifestStore(manifests=test_manifests)

    assert len(test_manifest_store.manifests) != 0
    assert len(test_manifest_store.content_boxes) != 0
