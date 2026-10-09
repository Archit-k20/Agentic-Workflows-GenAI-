"""Real upload -> parser -> adapter checks; only paid/model providers are mocked."""

import io
import json
from types import SimpleNamespace as NS
import pytest
import fitz
import docx
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient
from langchain_core.embeddings import Embeddings
from backend import app as module
from backend.storage import LocalStorage
from workflows import document_intelligence, document_qna, file_summarizer

TEXT = "TRACE SOURCE 2026. Review the proposal."


def fixture_bytes(suffix):
    if suffix == ".pdf":
        with fitz.open() as pdf:
            pdf.new_page().insert_text((40, 40), TEXT)
            return pdf.tobytes()
    stream = io.BytesIO()
    if suffix == ".docx":
        document = docx.Document()
        document.add_paragraph(TEXT)
        document.save(stream)
    elif suffix == ".txt":
        return TEXT.encode()
    else:
        image = Image.new("RGB", (1100, 160), "white")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        ImageDraw.Draw(image).text(
            (20, 40), "TRACE SOURCE 2026", font=font, fill="black"
        )
        image.save(stream, format="PNG" if suffix == ".png" else "JPEG")
    return stream.getvalue()


class MockEmbedding(Embeddings):
    def embed_documents(self, texts):
        assert all("TRACE SOURCE 2026" in text for text in texts)
        return [[float(len(text)), 1.0] for text in texts]

    def embed_query(self, text):
        return [float(len(text)), 1.0]


def result(response):
    assert response.status_code == 200
    blocks = response.text.split("\n\n")
    output = next(
        (block for block in blocks if block.startswith("event: result\n")), None
    )
    assert output, response.text
    return json.loads(output.split("data: ", 1)[1])


@pytest.mark.parametrize("suffix", [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"])
def test_supported_uploads_reach_real_parsers(tmp_path, monkeypatch, suffix):
    monkeypatch.setattr(module, "storage", LocalStorage(tmp_path))
    from backend.policy import Policy

    monkeypatch.setattr(module, "policy", Policy(module.storage))

    def analyze(**kwargs):
        assert "TRACE SOURCE 2026" in kwargs["messages"][-1]["content"]
        return NS(
            choices=[
                NS(
                    message=NS(
                        content=json.dumps(
                            {
                                "document_type": "Brief",
                                "summary": "Review the proposal",
                                "entities": {},
                                "action_items": [],
                                "risks": [],
                            }
                        )
                    )
                )
            ]
        )

    monkeypatch.setattr(
        document_intelligence,
        "OpenAI",
        lambda **kwargs: NS(chat=NS(completions=NS(create=analyze))),
    )
    monkeypatch.setattr(
        document_qna,
        "OpenAI",
        lambda **kwargs: NS(
            chat=NS(
                completions=NS(
                    create=lambda **kw: NS(
                        choices=[NS(message=NS(content="Fixture answer [S1]"))]
                    )
                )
            )
        ),
    )
    import langchain_openai

    monkeypatch.setattr(
        langchain_openai, "OpenAIEmbeddings", lambda **kwargs: MockEmbedding()
    )

    def summarize(text, **kwargs):
        assert "TRACE SOURCE 2026" in text
        assert kwargs == {"min_length": 100, "max_length": 300, "do_sample": False}
        return [{"summary_text": "Parsed fixture summary"}]

    monkeypatch.setattr(file_summarizer, "get_file_summary_pipeline", lambda: summarize)
    with TestClient(module.app) as client:
        token = client.post("/api/v1/sessions").json()["token"]
        headers = {
            "Authorization": "Bearer " + token,
            "X-OpenAI-Key": "mock-provider-key",
        }
        uploaded = client.post(
            "/api/v1/uploads",
            headers=headers,
            files={"file": ("fixture" + suffix, fixture_bytes(suffix))},
        )
        assert uploaded.status_code == 200
        ids = [uploaded.json()["file_id"]]
        intelligence = result(
            client.post(
                "/api/v1/runs",
                headers=headers,
                json={"tool": "documents", "file_ids": ids},
            )
        )
        assert not intelligence["errors"] and len(intelligence["documents"]) == 1
        if suffix in {".png", ".jpg", ".jpeg"}:
            ocr = result(
                client.post(
                    "/api/v1/runs",
                    headers=headers,
                    json={"tool": "ocr", "file_ids": ids},
                )
            )
            assert "TRACE SOURCE 2026" in ocr["text"]
        if suffix in {".pdf", ".docx"}:
            summary = result(
                client.post(
                    "/api/v1/runs",
                    headers=headers,
                    json={"tool": "file-summary", "file_ids": ids},
                )
            )
            assert summary["text"] == "Parsed fixture summary"
            context = result(
                client.post(
                    "/api/v1/contexts/documents",
                    headers=headers,
                    json={"file_ids": ids},
                )
            )
            answer = result(
                client.post(
                    "/api/v1/contexts/" + context["context_id"] + "/query",
                    headers=headers,
                    json={"question": "What needs review?"},
                )
            )
            assert "TRACE SOURCE 2026" in answer["sources"][0]["text"]
