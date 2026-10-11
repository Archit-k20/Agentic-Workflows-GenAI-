"""All fifteen adapters exercised with mocked providers, real parsers/index/checks."""

import base64
import io
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from PIL import Image
from pydantic import TypeAdapter
from backend import engine
from backend.storage import LocalStorage
from backend.contracts import RunInput
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
    support_triage,
    document_qna,
    url_qna,
)
from langchain_core.embeddings import Embeddings


class Embedding(Embeddings):
    def embed_documents(self, texts):
        return [[float(len(t)), 1.0] for t in texts]

    def embed_query(self, text):
        return [float(len(text)), 1.0]


@pytest.fixture
def harness(tmp_path, monkeypatch):
    storage = LocalStorage(tmp_path)
    session = storage.create_session()
    sid = storage.session(session["token"])
    responses = []
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        content = responses.pop(0) if responses else "A sourced answer. [S1]"
        return NS(
            choices=[
                NS(
                    message=NS(
                        content=json.dumps(content)
                        if isinstance(content, dict)
                        else content
                    )
                )
            ]
        )

    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buffer, format="PNG")
    image_call = Mock(
        return_value=NS(
            data=[NS(b64_json=base64.b64encode(buffer.getvalue()).decode())]
        )
    )
    speech_call = Mock(return_value=NS(content=b"fake-mp3"))
    client = NS(
        chat=NS(completions=NS(create=create)),
        images=NS(generate=image_call),
        audio=NS(speech=NS(create=speech_call)),
    )
    for module in [
        textsummary,
        image_gen,
        text_to_speech,
        code_copilot,
        content_pipeline,
        research_agent,
        document_intelligence,
        support_triage,
        document_qna,
        url_qna,
    ]:
        monkeypatch.setattr(module, "OpenAI", lambda **kwargs: client)
    for module, name in [
        (textsummary, "get_text_summary_pipeline"),
        (YT_summary, "get_text_summary_pipeline"),
        (article_summarizer, "get_article_summary_pipeline"),
        (file_summarizer, "get_file_summary_pipeline"),
    ]:
        monkeypatch.setattr(
            module, name, lambda: lambda *a, **kw: [{"summary_text": "Local summary"}]
        )

    class Article:
        text = "Readable source content. " * 300
        title = "Mock source"

        def __init__(self, url):
            self.url = url

        def download(self):
            pass

        def parse(self):
            pass

    for module in [article_summarizer, research_agent, support_triage, url_qna]:
        monkeypatch.setattr(module, "Article", Article)
    monkeypatch.setattr(YT_summary, "get_transcript", lambda _: "Transcript text")
    monkeypatch.setattr(
        yt_caption_generator, "get_transcript", lambda _: "Transcript text"
    )
    monkeypatch.setattr(
        image_to_text, "extract_text_from_image", lambda _: "Extracted image text"
    )
    import langchain_openai

    monkeypatch.setattr(
        langchain_openai, "OpenAIEmbeddings", lambda **kwargs: Embedding()
    )

    def add_file(name, data):
        item, folder = storage.put(sid, "upload", name)
        (folder / "file").write_bytes(data)
        return item

    import fitz

    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((40, 40), "TRACE source document. Please review the proposal.")
    pdf_id = add_file("brief.pdf", pdf.tobytes())
    pdf.close()
    txt_id = add_file("brief.txt", b"Mira Chen must review the plan by Oct 14.")
    image_id = add_file("input.png", buffer.getvalue())
    return (
        storage,
        sid,
        responses,
        calls,
        pdf_id,
        txt_id,
        image_id,
        image_call,
        speech_call,
    )


@pytest.mark.parametrize(
    "tool",
    [
        "text-summary",
        "youtube-summary",
        "article-summary",
        "file-summary",
        "ocr",
        "image",
        "speech",
        "captions",
        "code",
        "content",
        "research",
        "documents",
        "document-qa",
        "url-qa",
        "support",
    ],
)
def test_fifteen_tools(harness, tool):
    (
        storage,
        sid,
        responses,
        calls,
        pdf_id,
        txt_id,
        image_id,
        image_call,
        speech_call,
    ) = harness
    fields = {
        "tool": tool,
        "text": "Text to summarize",
        "prompt": "Create a function",
        "url": "https://youtu.be/abcdefghijk",
        "urls": ["https://example.com/article"],
        "idea": "Repair pilot",
        "topic": "Repair pilot",
        "question": "What should we review?",
        "file_ids": [pdf_id],
        "language": "python",
    }
    if tool == "ocr":
        fields["file_ids"] = [image_id]
    if tool == "documents":
        fields["file_ids"] = [txt_id]
        responses.append(
            {
                "document_type": "Brief",
                "summary": "Review the plan",
                "entities": {"people": ["Mira Chen"]},
                "action_items": [],
                "risks": [],
            }
        )
    elif tool == "code":
        responses.append(
            "def categories(items):\n    return list(dict.fromkeys(items))\n"
        )
    elif tool == "content":
        responses.extend(
            [
                {"content_angle": "Repair", "cta": "Book"},
                {
                    "title": "Repair",
                    "script": "Repair safely",
                    "captions": {"linkedin": "Repair"},
                    "image_prompts": ["tools"],
                    "hashtags": ["#Repair"],
                },
                {
                    "passes_review": True,
                    "issues": [],
                    "revised_script": "Repair safely",
                    "revised_captions": {"linkedin": "Repair"},
                },
            ]
        )
    elif tool == "research":
        responses.extend(
            [
                {"goal": "Repair", "sub_questions": []},
                {
                    "label": "S1",
                    "summary": "Evidence",
                    "key_points": [],
                    "relevance": "Relevant",
                },
                "Report [S1]",
                {"passes_review": True, "issues": [], "revised_report": "Report [S1]"},
            ]
        )
    elif tool == "support":
        responses.extend(
            [
                {"intent": "general", "requires_human": False},
                {"label": "S1", "summary": "Evidence", "key_points": []},
                {
                    "resolution_type": "answer",
                    "answer": "Resolution [S1]",
                    "confidence": 0.9,
                    "recommended_next_step": "Review",
                },
            ]
        )
    elif tool in {"document-qa", "url-qa"}:
        from backend.contracts import DocumentsContext, URLsContext

        inputs = (
            DocumentsContext(file_ids=[pdf_id])
            if tool == "document-qa"
            else URLsContext(urls=fields["urls"])
        )
        context = engine.context(storage, sid, tool, inputs, "mock-key")
        fields["context_id"] = context["context_id"]
    result = engine.execute(
        storage, sid, TypeAdapter(RunInput).validate_python(fields), "mock-key"
    )
    assert result["tool"] == tool
    if tool == "image":
        assert (
            image_call.call_args.kwargs["model"] == "gpt-image-1"
            and image_call.call_args.kwargs["size"] == "1024x1024"
        )
    if tool == "speech":
        assert (
            storage.get(sid, result["artifact_id"], "artifact")["folder"]
            .joinpath("file")
            .read_bytes()
            == b"fake-mp3"
        )
    if tool in {"document-qa", "url-qa"}:
        assert (
            result["sources"][0]["text"]
            and result["sources"][0]["metadata"]["chunk"] >= 1
        )
    if tool == "research":
        assert result["citation_check"]["cited_labels"] == ["S1"]
    if tool == "code":
        assert result["final_verification"]["passed"] and not result["repair_attempted"]
    if calls:
        assert all(c["model"] in {"gpt-3.5-turbo", "gpt-4o-mini"} for c in calls)
