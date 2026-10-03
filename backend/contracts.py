"""Discriminated contracts for all fifteen tools. Provider fields remain inspectable."""

from typing import Annotated, Literal, Union, Any
from pydantic import BaseModel, Field

Text = Annotated[str, Field(min_length=1, max_length=200000)]
URL = Annotated[str, Field(min_length=1, max_length=4096)]
Voice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
Language = Literal["python", "javascript", "java", "c", "c++"]


class TextSummary(BaseModel):
    tool: Literal["text-summary"]
    text: Text


class YoutubeSummary(BaseModel):
    tool: Literal["youtube-summary"]
    url: URL


class ArticleSummary(BaseModel):
    tool: Literal["article-summary"]
    url: URL


class FileSummary(BaseModel):
    tool: Literal["file-summary"]
    file_ids: list[str] = Field(min_length=1, max_length=1)


class OCR(BaseModel):
    tool: Literal["ocr"]
    file_ids: list[str] = Field(min_length=1, max_length=1)


class ImageGeneration(BaseModel):
    tool: Literal["image"]
    prompt: Text


class Speech(BaseModel):
    tool: Literal["speech"]
    text: Text
    voice: Voice = "alloy"


class Captions(BaseModel):
    tool: Literal["captions"]
    url: URL


class Code(BaseModel):
    tool: Literal["code"]
    prompt: Text
    language: Language = "python"


class Content(BaseModel):
    tool: Literal["content"]
    idea: Text
    tone: Literal[
        "professional", "playful", "educational", "launch-ready", "social-first"
    ] = "professional"
    platforms: list[Literal["linkedin", "x", "instagram", "youtube", "blog"]] = Field(
        default=["linkedin", "x"], min_length=1, max_length=5
    )
    include_audio: bool = False
    voice: Voice = "alloy"


class Research(BaseModel):
    tool: Literal["research"]
    topic: Text
    urls: list[str] = Field(min_length=1, max_length=5)


class Intelligence(BaseModel):
    tool: Literal["documents"]
    file_ids: list[str] = Field(min_length=1, max_length=3)


class DocumentQA(BaseModel):
    tool: Literal["document-qa"]
    context_id: str
    question: Text


class URLQA(BaseModel):
    tool: Literal["url-qa"]
    context_id: str
    question: Text


class Support(BaseModel):
    tool: Literal["support"]
    question: Text
    urls: list[str] = Field(min_length=1, max_length=5)


RunInput = Annotated[
    Union[
        TextSummary,
        YoutubeSummary,
        ArticleSummary,
        FileSummary,
        OCR,
        ImageGeneration,
        Speech,
        Captions,
        Code,
        Content,
        Research,
        Intelligence,
        DocumentQA,
        URLQA,
        Support,
    ],
    Field(discriminator="tool"),
]


class Source(BaseModel):
    label: str
    title: str = ""
    url: str = ""
    summary: str = ""
    key_points: list[str] = []
    relevance: str = ""
    text: str = ""
    metadata: dict[str, Any] = {}


class CitationCheck(BaseModel):
    has_any_citation: bool
    cited_labels: list[str]
    unknown_labels: list[str]


class Check(BaseModel):
    name: str
    passed: bool
    details: str


class Verification(BaseModel):
    language: str
    passed: bool
    checks: list[Check]


class TextResult(BaseModel):
    tool: Literal[
        "text-summary",
        "youtube-summary",
        "article-summary",
        "file-summary",
        "ocr",
        "captions",
    ]
    text: str


class ArtifactResult(BaseModel):
    tool: Literal["image", "speech"]
    artifact_id: str
    media_type: str


class CodeResult(BaseModel):
    tool: Literal["code"]
    language: str
    initial_code: str
    final_code: str
    repair_attempted: bool
    initial_verification: Verification
    final_verification: Verification


class ResearchResult(BaseModel):
    tool: Literal["research"]
    plan: dict[str, Any]
    sources: list[Source]
    source_errors: list[dict[str, str]]
    invalid_urls: list[str]
    draft_report: str
    final_report: str
    critique: dict[str, Any]
    citation_check: CitationCheck


class ContentResult(BaseModel):
    tool: Literal["content"]
    plan: dict[str, Any]
    package: dict[str, Any]
    critique: dict[str, Any]
    final_script: str
    final_captions: dict[str, str]
    audio_path: str | None
    audio_error: str | None
    artifact_id: str | None = None


class DocumentResult(BaseModel):
    tool: Literal["documents"]
    documents: list[dict[str, Any]]
    errors: list[dict[str, str]]


class QAResult(BaseModel):
    tool: Literal["document-qa", "url-qa"]
    answer: str
    sources: list[Source]


class SupportResult(BaseModel):
    tool: Literal["support"]
    intent: dict[str, Any]
    sources: list[Source]
    source_errors: list[dict[str, str]]
    invalid_urls: list[str]
    draft: dict[str, Any]
    final: dict[str, Any]


RunResult = Annotated[
    Union[
        TextResult,
        ArtifactResult,
        CodeResult,
        ResearchResult,
        ContentResult,
        DocumentResult,
        QAResult,
        SupportResult,
    ],
    Field(discriminator="tool"),
]


class DocumentsContext(BaseModel):
    file_ids: list[str] = Field(min_length=1, max_length=3)


class URLsContext(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=3)


class Query(BaseModel):
    question: Text


class ContextResult(BaseModel):
    context_id: str
    errors: list[str]
    kind: Literal["document-qa", "url-qa"]


class WorkflowEvent(BaseModel):
    event: Literal["started", "stage", "warning", "result", "error"]
    data: RunResult | ContextResult | dict[str, Any]
