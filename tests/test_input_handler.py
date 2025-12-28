import os
import tempfile
import warnings

import pytest

from app.input_handler import load_images


def test_empty_list_raises():
    with pytest.raises(ValueError):
        load_images([])


def test_valid_local_and_url(tmp_path):
    # create a temporary jpg file
    p = tmp_path / "img1.jpg"
    p.write_bytes(b"JPEGDATA")

    inputs = [str(p), "http://example.com/path/pic.png", "http://example.com/invalid.txt", "/non/existent.jpg", ""]

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = load_images(inputs)

    # Only the valid local and the valid URL should be returned
    assert len(res) == 2
    types = {r["type"] for r in res}
    assert types == {"local", "url"}
    assert all("id" in r and "source" in r for r in res)


def test_deterministic_ids(tmp_path):
    p = tmp_path / "a.png"
    p.write_bytes(b"PNG")
    r1 = load_images([str(p)])
    r2 = load_images([str(p)])
    assert r1[0]["id"] == r2[0]["id"]
