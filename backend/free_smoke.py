"""Real, pinned CPU embedding/index/speech checks; optional Ollama inference."""

import argparse
import tempfile
from pathlib import Path
import numpy as np
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from .retrieval import LocalEmbeddings, PROFILE, retrieve
from .engine import save_index, load_index
from .speech import synthesize
from .providers import Runtime

parser = argparse.ArgumentParser()
parser.add_argument("--ollama", action="store_true")
args = parser.parse_args()
embedding = LocalEmbeddings()
vectors = embedding.embed_documents(
    ["Alder ships 32 kits.", "Birch ships 40 repair kits."]
)
assert np.asarray(vectors).shape == (2, 384)
assert np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)
store = FAISS.from_documents(
    [
        Document(
            page_content="Alder ships 32 kits.",
            metadata={"source": "brief", "chunk": 1},
        ),
        Document(
            page_content="Birch ships 40 repair kits.",
            metadata={"source": "brief", "chunk": 2},
        ),
    ],
    embedding,
    normalize_L2=True,
)
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    save_index(store, folder)
    restored = load_index(folder, "", PROFILE)
    result = retrieve(restored, "How many kits does Alder ship?")
    assert result and any("32 kits" in d.page_content for d in result)
    synthesize("Trace is ready.", "af_heart", folder / "voice.mp3")
    import subprocess

    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(folder / "voice.mp3"), "-f", "null", "-"],
        check=True,
        capture_output=True,
        timeout=30,
    )
    assert (folder / "voice.mp3").stat().st_size > 1000
print(
    "Real normalized BGE, FAISS/JSON restart, hybrid retrieval and Kokoro MP3 checks passed.",
    flush=True,
)
if args.ollama:
    runtime = Runtime("local", "readiness")
    output = runtime.local_text(
        [
            {"role": "system", "content": "Reply in one short sentence."},
            {
                "role": "user",
                "content": "The brief says Alder ships 32 kits. Repeat only the quantity and item.",
            },
        ],
        64,
        False,
        0,
    )
    assert "32" in output and output.strip()
    structured = runtime.create(
        messages=[
            {
                "role": "system",
                "content": "Return JSON with goal, sub_questions, and report_sections.",
            },
            {
                "role": "user",
                "content": "Goal: summarize a brief. Use one sub-question and one section.",
            },
        ],
        response_format={"type": "json_object"},
    )
    import json

    parsed = json.loads(structured.choices[0].message.content)
    assert isinstance(parsed["goal"], str) and all(
        isinstance(item, str) for item in parsed["sub_questions"]
    )
    print(
        "Pinned CPU Ollama inference and constrained JSON generation passed.",
        flush=True,
    )
