import pytest

from tc_c2pa_py.c2pa.manifest import Manifest
from tc_c2pa_py.utils.content_types import c2pa_content_types

def test_create_manifest():

    test_manifest = Manifest()

    assert test_manifest != None
    assert test_manifest.claim == None
    assert test_manifest.claim_signature == None
    assert test_manifest.assertion_store == None
    assert len(test_manifest.content_boxes) == 0


def test_create_manifest_with_jumb_base_type():

    test_manifest = Manifest()

    assert test_manifest.t_box == 'jumb'.encode('utf-8').hex()
    assert test_manifest.get_content_type() == c2pa_content_types["default_manifest"]
    # assert test_manifest.description_box.label == '' # TODO: find out what label should be setted


def test_create_manifest_with_creation_content_boxes():

    test_manifest = Manifest()

    test_manifest.set_claim(None)
    
    assert len(test_manifest.content_boxes) != 0