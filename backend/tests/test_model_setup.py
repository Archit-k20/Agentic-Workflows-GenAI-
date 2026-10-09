import hashlib
import io
import json
from pathlib import Path

import pytest
from backend import install_local_model as setup


class Response(io.BytesIO):
    def geturl(self):
        return "https://registry.ollama.ai/test"


def fixture(tmp_path, monkeypatch):
    data = b"fixed model content"
    descriptor = {"digest": "sha256:" + hashlib.sha256(data).hexdigest(), "size": len(data)}
    raw = json.dumps({"config": descriptor, "layers": []}).encode()
    monkeypatch.setattr(setup, "LOCAL_DIGEST", hashlib.sha256(raw).hexdigest())
    pin = tmp_path / "pin.json"
    pin.write_bytes(raw)
    return data, descriptor, pin, tmp_path / "models"


def test_bundled_manifest_is_exact_tested_digest():
    assert hashlib.sha256(setup.PIN.read_bytes()).hexdigest() == setup.LOCAL_DIGEST


def test_mutable_or_tampered_manifest_stops_before_download(tmp_path):
    pin = tmp_path / "manifest"
    pin.write_bytes(b"{}")
    with pytest.raises(ValueError, match="differs from the tested pin"):
        setup.install(tmp_path / "models", pin, lambda *a, **k: pytest.fail("must not download"))
    assert not (tmp_path / "models").exists()


def test_exact_blobs_and_raw_manifest_are_installed_atomically(tmp_path, monkeypatch):
    data, entry, pin, models = fixture(tmp_path, monkeypatch)
    report = setup.install(models, pin, lambda *a, **k: Response(data))
    assert report["downloaded_blobs"] == 1
    assert (models / "blobs" / entry["digest"].replace(":", "-")).read_bytes() == data
    assert (models / "manifests/registry.ollama.ai/library/qwen3.5/4b").read_bytes() == pin.read_bytes()
    report = setup.install(models, pin, lambda *a, **k: pytest.fail("cached checksum should avoid download"))
    assert report["downloaded_blobs"] == 0


@pytest.mark.parametrize("received", [b"short", b"wrong model content", b"oversized model content is rejected"])
def test_bad_download_never_replaces_existing_manifest_or_leaves_temp_files(tmp_path, monkeypatch, received):
    _, _, pin, models = fixture(tmp_path, monkeypatch)
    target = models / "manifests/registry.ollama.ai/library/qwen3.5/4b"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"prior manifest")
    with pytest.raises(ValueError, match="checksum/size mismatch|exceeds"):
        setup.install(models, pin, lambda *a, **k: Response(received))
    assert target.read_bytes() == b"prior manifest"
    assert not list((models / "blobs").glob(".trace-download-*"))


def test_corrupt_cached_blob_is_repaired_not_trusted_by_size(tmp_path, monkeypatch):
    data, entry, pin, models = fixture(tmp_path, monkeypatch)
    destination = models / "blobs" / entry["digest"].replace(":", "-")
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"x" * len(data))
    assert setup.install(models, pin, lambda *a, **k: Response(data))["downloaded_blobs"] == 1
    assert destination.read_bytes() == data


def test_invalid_descriptors_never_become_paths(tmp_path, monkeypatch):
    raw = json.dumps({"config": {"digest": "../../bad", "size": 10}, "layers": []}).encode()
    monkeypatch.setattr(setup, "LOCAL_DIGEST", hashlib.sha256(raw).hexdigest())
    pin = tmp_path / "pin"
    pin.write_bytes(raw)
    with pytest.raises(ValueError, match="Invalid pinned blob"):
        setup.install(tmp_path / "models", pin)
    assert not (tmp_path / "models").exists()
