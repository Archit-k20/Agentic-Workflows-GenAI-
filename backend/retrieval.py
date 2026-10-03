"""Local CLS embeddings, immutable profiles, semantic + BM25 fusion."""

import math
import re
from functools import lru_cache
from collections import Counter
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from . import free_config as cfg
from .processing import tokenizer, chunks, extract, article

PROFILE = {
    "version": 1,
    "model": cfg.EMBED_MODEL,
    "revision": cfg.EMBED_REVISION,
    "dimensions": 384,
    "normalized": True,
    "chunk_tokens": 384,
    "overlap": 64,
}


@lru_cache(maxsize=1)
def model():
    from transformers import AutoModel

    with cfg.CPU_GATE:
        return AutoModel.from_pretrained(
            cfg.EMBED_MODEL, revision=cfg.EMBED_REVISION
        ).eval()


class LocalEmbeddings(Embeddings):
    def embed_documents(self, texts):
        import torch
        import torch.nn.functional as F

        result = []
        with cfg.CPU_GATE, torch.inference_mode():
            tok = tokenizer()
            for start in range(0, len(texts), 16):
                batch = texts[start : start + 16]
                if any(len(tok.encode(t, verbose=False)) > 512 for t in batch):
                    raise ValueError(
                        "Embedding input exceeds 512 tokens; reprocess context."
                    )
                inputs = tok(batch, padding=True, truncation=False, return_tensors="pt")
                vectors = F.normalize(
                    model()(**inputs).last_hidden_state[:, 0], p=2, dim=1
                )
                result.extend(vectors.tolist())
        return result

    def embed_query(self, text):
        return self.embed_documents(
            ["Represent this sentence for searching relevant passages: " + text]
        )[0]


def build(kind, files, urls, runtime):
    docs, errors = [], []
    for source in (files if kind == "document-qa" else urls):
        try:
            item = (
                extract(source, runtime)
                if kind == "document-qa"
                else article(source, runtime)
            )
            label = item.get("name", item.get("url"))
            for i, part in enumerate(chunks(item["text"], 384, 64)):
                docs.append(
                    Document(
                        page_content=part,
                        metadata={
                            "source": label,
                            "title": item.get("title", label),
                            "chunk": i + 1,
                        },
                    )
                )
        except Exception as exc:
            errors.append(f"{getattr(source,'name',source)}: {exc}")
    if not docs:
        raise ValueError("No readable context could be processed. " + "; ".join(errors))
    runtime.expensive = True
    runtime.record("local", cfg.EMBED_MODEL)
    return FAISS.from_documents(docs, LocalEmbeddings(), normalize_L2=True), errors


def retrieve(store, question):
    docs = [
        store.docstore.search(store.index_to_docstore_id[i])
        for i in range(store.index.ntotal)
    ]
    semantic = store.similarity_search(question, k=min(12, len(docs)))
    tokens = lambda t: re.findall(r"\w+", t.lower())
    counts = [Counter(tokens(d.page_content)) for d in docs]
    avg = sum(sum(c.values()) for c in counts) / max(1, len(counts))
    q = set(tokens(question))
    scores = []
    for i, c in enumerate(counts):
        score = 0
        for term in q:
            frequency = sum(term in x for x in counts)
            tf = c.get(term, 0)
            idf = math.log(1 + (len(docs) - frequency + 0.5) / (frequency + 0.5))
            score += (
                idf
                * tf
                * 2.5
                / (tf + 1.5 * (0.25 + 0.75 * sum(c.values()) / max(1, avg)))
            )
        scores.append((score, i))
    ranked = {}
    lookup = {id(d): i for i, d in enumerate(docs)}
    for rank, d in enumerate(semantic, 1):
        # Restored FAISS documents are the same objects in its docstore.
        i = lookup[id(d)]
        ranked[i] = ranked.get(i, 0) + 1 / (60 + rank)
    for rank, (score, i) in enumerate(sorted(scores, reverse=True)[:12], 1):
        if score > 0:
            ranked[i] = ranked.get(i, 0) + 1 / (60 + rank)
    return [docs[i] for i in sorted(ranked, key=lambda i: (-ranked[i], i))[:4]]
