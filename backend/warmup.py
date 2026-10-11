"""Download and validate pinned local assets before admitting portfolio traffic."""

import os
from pathlib import Path
from .processing import tokenizer
from .retrieval import LocalEmbeddings
from .speech import pipeline
from .providers import Runtime
from .free_config import LOCAL_MODEL


def main():
    tokenizer()
    vectors = LocalEmbeddings().embed_documents(["TRACE readiness check"])
    assert len(vectors[0]) == 384
    print("Pinned BGE tokenizer and embeddings ready.", flush=True)
    pipeline("a")
    pipeline("b")
    print("Pinned Kokoro voices and English phonemizer ready.", flush=True)
    runtime = Runtime("local", "readiness")
    text = runtime.local_text(
        [
            {"role": "system", "content": "Reply briefly."},
            {"role": "user", "content": "Say ready."},
        ],
        16,
        False,
        0,
    )
    if not text.strip():
        raise RuntimeError("Local model returned no readiness text.")
    print("Pinned Ollama model ready: " + LOCAL_MODEL, flush=True)


if __name__ == "__main__":
    main()
