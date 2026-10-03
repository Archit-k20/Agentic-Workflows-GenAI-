"""One CPU model, serialized inference, original per-tool parameters."""

from backend.free_config import CPU_GATE

_lock = CPU_GATE
_model = None


def get_pipeline():
    global _model
    with _lock:
        if _model is None:
            from transformers import pipeline

            _model = pipeline(
                "summarization", model="sshleifer/distilbart-cnn-12-6", device=-1
            )

    def infer(*args, **kwargs):
        with _lock:
            return _model(*args, **kwargs)

    return infer
