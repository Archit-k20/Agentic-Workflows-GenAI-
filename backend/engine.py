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

    def __getattr__(self, name):
        # PIL, PDF readers and ZIP/DOCX parsers also need tell/readline/seekable.
        return getattr(self.file, name)

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


def load_index(folder, key, profile=None):
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
    from .retrieval import LocalEmbeddings, PROFILE

    if profile and profile != PROFILE:
        raise ValueError(
            "Context embedding profile changed. Reprocess your files or URLs."
        )
    return FAISS(
        LocalEmbeddings() if profile else OpenAIEmbeddings(api_key=key),
        faiss.read_index(str(folder / "index.faiss")),
        docstore,
        {i: str(i) for i in range(len(docs))},
    )


def context(storage, session, kind, inputs, key):
    from workflows import document_qna, url_qna

    from workflows.runtime import current

    runtime = current.get()
    free = runtime is not None and runtime.mode != "openai"
    emit("stage", name="Extract and index context", status="running")
    with ExitStack() as stack:
        if kind == "document-qa":
            uploaded = files(
                storage, session, inputs.file_ids, stack, {".pdf", ".docx"}
            )
            if free:
                from .retrieval import build

                store, errors = build(kind, uploaded, [], runtime)
            else:
                store, errors = document_qna.build_document_vectorstore(uploaded, key)
        else:
            urls = [u for u in inputs.urls if url_qna.is_valid_url(u)]
            if not urls:
                raise ValueError("Enter at least one valid HTTP or HTTPS URL.")
            if free:
                from .retrieval import build

                store, errors = build(kind, [], urls, runtime)
            else:
                store, errors = url_qna.build_url_vectorstore(urls, key)
    from .retrieval import PROFILE

    profile = PROFILE if free else None
    item, folder = storage.put(
        session,
        "context",
        kind,
        {"mode": "free" if free else "openai", "profile": profile},
    )
    save_index(store, folder)
    for error in errors:
        emit("warning", message=error)
    emit("stage", name="Extract and index context", status="completed")
    return {
        "context_id": item,
        "errors": errors,
        "kind": kind,
        "profile": profile,
        "execution": runtime.metadata() if runtime else None,
    }


def query(storage, session, item, question, key, expected=None):
    from workflows import document_qna, url_qna

    row = storage.get(session, item, "context")
    if expected and row["name"] != expected:
        raise ValueError("This context belongs to a different Q&A tool.")
    emit("stage", name="Retrieve four relevant chunks", status="running")
    from workflows.runtime import current

    runtime = current.get()
    free = runtime is not None and runtime.mode != "openai"
    profile = row["metadata"].get("profile")
    if free != bool(profile):
        raise ValueError(
            "This context uses a different execution profile. Reprocess your files or URLs in the selected mode."
        )
    store = load_index(row["folder"], key, profile)
    if free:
        from .retrieval import retrieve

        runtime.expensive = True
        from .free_config import EMBED_MODEL

        runtime.record("local", EMBED_MODEL)
        docs = retrieve(store, question)
    else:
        docs = store.similarity_search(question, k=4)
    emit("stage", name="Retrieve four relevant chunks", status="completed")
    emit("stage", name="Answer from context", status="running")
    module = document_qna if row["name"] == "document-qa" else url_qna
    if free:
        from .processing import check_text

        check_text(question, runtime, "Question")
    answer = module.answer_with_context(question, docs, key)
    if free:
        import re

        labels = {f"S{i+1}" for i in range(len(docs))}
        if set(re.findall(r"\[(S\d+)\]", answer)) - labels:
            raise ValueError(
                "The answer contains unknown citation labels. No answer was accepted; retry explicitly."
            )
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
    if runtime:
        result["execution"] = runtime.metadata()
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

    from workflows.runtime import current

    runtime = current.get()
    free = runtime is not None and runtime.mode != "openai"
    tool = inputs.tool
    if free:
        from .processing import check_text

        for field in ("topic", "question", "idea", "text", "transcript_text"):
            value = getattr(inputs, field, None)
            if value:
                check_text(value, runtime, field.replace("_", " "))
        if tool == "code":
            check_text(inputs.prompt, runtime, "Code task")
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
        and not free
    ):
        raise ValueError("Enter an OpenAI API key in Settings before live execution.")
    if tool in {"speech", "content"}:
        inputs.voice = inputs.voice or ("af_heart" if free else "alloy")
        from .free_config import VOICES, OPENAI_VOICES

        allowed = {v["id"] for v in VOICES} if free else set(OPENAI_VOICES)
        if inputs.voice not in allowed:
            raise ValueError("Choose a voice for the selected execution mode.")
    with ExitStack() as stack:
        if free and tool in {
            "text-summary",
            "youtube-summary",
            "article-summary",
            "file-summary",
            "ocr",
            "captions",
            "image",
            "speech",
        }:
            result = free_simple(storage, session, inputs, runtime, stack)
        elif tool == "research":
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
                    text = (
                        YT_summary.get_text_summary_pipeline()(
                            inputs.transcript_text[:4000],
                            min_length=100,
                            max_length=300,
                            do_sample=False,
                        )[0]["summary_text"]
                        if inputs.transcript_text
                        else YT_summary.summarize_from_url(inputs.url, key)
                    )
                elif tool == "article-summary":
                    text = article_summarizer.summarize_article(inputs.url, key)
                elif tool == "captions":
                    text = (
                        inputs.transcript_text
                        or yt_caption_generator.caption_from_youtube_url(inputs.url)
                    )
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
    if runtime:
        if runtime.mode == "openai":
            if tool in {"youtube-summary", "article-summary", "file-summary"}:
                runtime.record("local", "sshleifer/distilbart-cnn-12-6")
            elif tool in {"ocr", "captions"}:
                runtime.record(
                    "local", "tesseract" if tool == "ocr" else "youtube-transcript-api"
                )
            else:
                runtime.record(
                    "openai",
                    {
                        "image": "gpt-image-1",
                        "speech": "tts-1",
                        "text-summary": "gpt-3.5-turbo",
                    }.get(tool, "gpt-4o-mini"),
                )
        result["execution"] = runtime.metadata()
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


def free_simple(storage, session, inputs, runtime, stack):
    from .processing import extract, article, summarize, check_text

    tool = inputs.tool
    if tool == "image":
        image = runtime.image(inputs.prompt)
        item, folder = storage.put(
            session, "artifact", "image/png", {"media_type": "image/png"}
        )
        image.save(folder / "file", format="PNG")
        return {
            "artifact_id": item,
            "media_type": "image/png",
            "width": image.width,
            "height": image.height,
        }
    if tool == "speech":
        _, folder = storage.put(session, "temporary", "speech")
        path = runtime.speech(inputs.text, inputs.voice, folder / "file")
        return {
            "artifact_id": artifact(storage, session, path, "audio/mpeg"),
            "media_type": "audio/mpeg",
        }
    if tool in {"file-summary", "ocr"}:
        extensions = (
            {".pdf", ".docx"} if tool == "file-summary" else {".png", ".jpg", ".jpeg"}
        )
        item = files(storage, session, inputs.file_ids, stack, extensions)[0]
        text = extract(item, runtime)["text"]
    elif tool == "article-summary":
        text = article(inputs.url, runtime)["text"]
    elif tool in {"youtube-summary", "captions"}:
        if inputs.transcript_text:
            text = inputs.transcript_text
        else:
            from workflows.yt_caption_generator import caption_from_youtube_url

            runtime.expensive = True
            emit("stage", name="Extract YouTube transcript", status="running")
            text = ensure_text(caption_from_youtube_url(inputs.url))
            emit("stage", name="Extract YouTube transcript", status="completed")
    else:
        text = inputs.text
    if tool in {"ocr", "captions"}:
        check_text(text, runtime, "Extracted text")
        return {"text": text}
    return {"text": summarize(text, runtime)}
