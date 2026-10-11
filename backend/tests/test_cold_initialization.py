"""Concurrent cold starts must initialize each shared Transformers asset once."""
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import pytest

@pytest.mark.parametrize("module_name,public_name,cached_name,factory_name", [
    ("processing", "tokenizer", "_tokenizer", "AutoTokenizer"),
    ("retrieval", "model", "_model", "AutoModel"),
])
def test_concurrent_cold_asset_is_initialized_once(monkeypatch, module_name, public_name, cached_name, factory_name):
    import importlib
    import transformers
    module = importlib.import_module("backend." + module_name)
    cached = getattr(module, cached_name)
    cached.cache_clear()
    calls = []
    barrier = threading.Barrier(2)
    shared = SimpleNamespace(eval=lambda: shared)
    def create(*args, **kwargs):
        calls.append(kwargs)
        time.sleep(0.05)  # expose a duplicate cold cache miss if not serialized
        return shared
    monkeypatch.setattr(transformers, factory_name, SimpleNamespace(from_pretrained=create))
    def load():
        barrier.wait(timeout=5)
        return getattr(module, public_name)()
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first, second = pool.submit(load), pool.submit(load)
            assert first.result(timeout=5) is shared
            assert second.result(timeout=5) is shared
        assert len(calls) == 1
        assert calls[0]["revision"] == module.cfg.EMBED_REVISION
    finally:
        cached.cache_clear()
