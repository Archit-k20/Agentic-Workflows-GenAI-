"""Adapter: original workflow calls, safe index persistence, session artifacts."""

import json
import os
from contextlib import ExitStack
from pathlib import Path
from pydantic import TypeAdapter
from .contracts import RunResult
from .events import emit


class NamedFile:
    def __init__(self, path, name):
        self.file = open(path, "rb")
        self.name = name

    def read(self, *args):
        return self.file.read(*args)

    def seek(self, *args):
        return self.file.seek(*args)

    def close(self):
        self.file.close()


def files(storage, session, ids, stack, extensions):
    result = []
    for item in ids:
        row = storage.get(session, item, "upload")
        if Path(row["name"]).suffix.lower() not in extensions:
            raise ValueError(
                "Unsupported file for this tool. Choose " + ", ".join(extensions) + "."
            )
        file = NamedFile(row["folder"] / "file", row["name"])
        stack.callback(file.close)
        result.append(file)
    return result


def save_index(store, folder):
    import faiss

    # Never call LangChain save_local/load_local: their docstore uses pickle.
    faiss.write_index(store.index, str(folder / "index.faiss"))
    documents = []
    for index in range(store.index.ntotal):
        doc = store.docstore.search(store.index_to_docstore_id[index])
        documents.append({"text": doc.page_content, "metadata": doc.metadata})
    (folder / "documents.json").write_text(json.dumps(documents), encoding="utf-8")


def load_index(folder, key):
    import faiss
    from langchain_core.documents import Document
    from langchain_community.docstore.in_memory import InMemoryDocstore
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings

    docs = json.loads((folder / "documents.json").read_text(encoding="utf-8"))
    docstore = InMemoryDocstore(
        {
            str(i): Document(page_content=d["text"], metadata=d["metadata"])
            for i, d in enumerate(docs)
        }
    )
    return FAISS(
        OpenAIEmbeddings(api_key=key),
        faiss.read_index(str(folder / "index.faiss")),
        docstore,
        {i: str(i) for i in range(len(docs))},
    )


def context(storage, session, kind, inputs, key):
    from workflows import document_qna, url_qna

    emit("stage", name="Extract and index context", status="running")
    with ExitStack() as stack:
        if kind == "document-qa":
            uploaded = files(
                storage, session, inputs.file_ids, stack, {".pdf", ".docx"}
            )
            store, errors = document_qna.build_document_vectorstore(uploaded, key)
        else:
            urls = [u for u in inputs.urls if url_qna.is_valid_url(u)]
            if not urls:
                raise ValueError("Enter at least one valid HTTP or HTTPS URL.")
            store, errors = url_qna.build_url_vectorstore(urls, key)
    item, folder = storage.put(session, "context", kind)
    save_index(store, folder)
    for error in errors:
        emit("warning", message=error)
    emit("stage", name="Extract and index context", status="completed")
    return {"context_id": item, "errors": errors, "kind": kind}


def query(storage, session, item, question, key, expected=None):
    from workflows import document_qna, url_qna

    row = storage.get(session, item, "context")
    if expected and row["name"] != expected:
        raise ValueError("This context belongs to a different Q&A tool.")
    emit("stage", name="Retrieve four relevant chunks", status="running")
    store = load_index(row["folder"], key)
    docs = store.similarity_search(question, k=4)
    emit("stage", name="Retrieve four relevant chunks", status="completed")
    emit("stage", name="Answer from context", status="running")
    module = document_qna if row["name"] == "document-qa" else url_qna
    answer = module.answer_with_context(question, docs, key)
    emit("stage", name="Answer from context", status="completed")
    result = {
        "tool": row["name"],
        "answer": answer,
        "sources": [
            {
                "label": f"S{i + 1}",
                "title": d.metadata.get("title", d.metadata.get("source", "")),
                "url": d.metadata.get("source", "") if row["name"] == "url-qa" else "",
                "text": d.page_content,
                "metadata": d.metadata,
            }
            for i, d in enumerate(docs)
        ],
    }
    return TypeAdapter(RunResult).validate_python(result).model_dump()


def artifact(storage, session, path, kind):
    import shutil

    item, folder = storage.put(session, "artifact", kind, {"media_type": kind})
    shutil.move(str(path), str(folder / "file"))
    return item


def ensure_text(value):
    if not isinstance(value, str):
        raise ValueError("The provider returned no readable output.")
    if value.startswith(
        (
            "Error",
            "Invalid YouTube",
            "Could not extract",
            "The file appears",
            "Unsupported file",
            "No text could",
        )
    ):
        raise ValueError(value)
    return value


def execute(storage, session, inputs, key):
    from workflows import (
        textsummary,
        YT_summary,
        article_summarizer,
        file_summarizer,
        image_to_text,
        image_gen,
        text_to_speech,
        yt_caption_generator,
        code_copilot,
        content_pipeline,
        research_agent,
        document_intelligence,
    )

    tool = inputs.tool
    if (
        tool
        not in {
            "text-summary",
            "youtube-summary",
            "article-summary",
            "file-summary",
            "ocr",
        }
        and not key
    ):
        raise ValueError("Enter an OpenAI API key in Settings before live execution.")
    with ExitStack() as stack:
        if tool == "research":
            result = research_agent.run_research_agent(inputs.topic, inputs.urls, key)
        elif tool == "support":
            from workflows.support_triage import run_support_triage

            result = run_support_triage(inputs.question, inputs.urls, key)
        elif tool == "documents":
            result = document_intelligence.run_document_intelligence(
                files(
                    storage,
                    session,
                    inputs.file_ids,
                    stack,
                    {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"},
                ),
                key,
            )
        elif tool == "code":
            result = code_copilot.run_code_copilot(inputs.prompt, key, inputs.language)
        elif tool == "content":
            audio_path = None
            if inputs.include_audio:
                _, folder = storage.put(session, "temporary", "narration")
                audio_path = folder / "file"
            result = content_pipeline.run_content_pipeline(
                inputs.idea,
                inputs.tone,
                inputs.platforms,
                key,
                inputs.include_audio,
                inputs.voice,
                audio_output_path=audio_path,
            )
            if result["audio_path"]:
                item = artifact(storage, session, result["audio_path"], "audio/mpeg")
                result["audio_path"] = item
                result["artifact_id"] = item
        elif tool in {"document-qa", "url-qa"}:
            return query(
                storage, session, inputs.context_id, inputs.question, key, tool
            )
        else:
            label = {
                "image": "Generate image",
                "speech": "Generate speech",
                "ocr": "Extract image text",
                "captions": "Extract transcript",
            }.get(tool, "Extract and summarize")
            emit("stage", name=label, status="running")
            if tool == "image":
                image = image_gen.generate_image_from_text(inputs.prompt, key)
                if isinstance(image, str):
                    raise ValueError(image)
                item, folder = storage.put(
                    session, "artifact", "image/png", {"media_type": "image/png"}
                )
                image.save(folder / "file", format="PNG")
                result = {"artifact_id": item, "media_type": "image/png"}
            elif tool == "speech":
                _, folder = storage.put(session, "temporary", "speech")
                path = ensure_text(
                    text_to_speech.generate_speech(
                        inputs.text, inputs.voice, key, output_path=folder / "file"
                    )
                )
                result = {
                    "artifact_id": artifact(storage, session, path, "audio/mpeg"),
                    "media_type": "audio/mpeg",
                }
            else:
                if tool == "text-summary":
                    text = textsummary.summary(inputs.text, key)
                elif tool == "youtube-summary":
                    text = YT_summary.summarize_from_url(inputs.url, key)
                elif tool == "article-summary":
                    text = article_summarizer.summarize_article(inputs.url, key)
                elif tool == "captions":
                    text = yt_caption_generator.caption_from_youtube_url(inputs.url)
                elif tool == "file-summary":
                    text = file_summarizer.summarize_file(
                        files(
                            storage, session, inputs.file_ids, stack, {".pdf", ".docx"}
                        )[0],
                        key,
                    )
                else:
                    text = image_to_text.extract_text_from_image(
                        files(
                            storage,
                            session,
                            inputs.file_ids,
                            stack,
                            {".png", ".jpg", ".jpeg"},
                        )[0]
                    )
                result = {"text": ensure_text(text)}
            emit("stage", name=label, status="completed")
    result["tool"] = tool
    if tool == "code" and not result["final_verification"]["passed"]:
        emit(
            "warning",
            message="Final syntax/compilation checks failed or were unavailable. Inspect each check before using the code.",
        )
    if tool in {"research", "content"} and not result["critique"].get(
        "passes_review", False
    ):
        emit(
            "warning",
            message="The model review still flags issues. Inspect the review details.",
        )
    if tool == "research" and (
        not result["citation_check"]["has_any_citation"]
        or result["citation_check"]["unknown_labels"]
    ):
        emit(
            "warning",
            message="Citation-label validation did not pass. Inspect missing or unknown labels.",
        )
    for field in ["source_errors", "errors", "invalid_urls"]:
        for error in result.get(field, []):
            emit(
                "warning",
                message=json.dumps(error) if isinstance(error, dict) else str(error),
            )
    if result.get("audio_error"):
        emit("warning", message=result["audio_error"])
    return TypeAdapter(RunResult).validate_python(result).model_dump()
