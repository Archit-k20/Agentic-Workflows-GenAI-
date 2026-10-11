# TRACE tool contracts

All fifteen tools are exposed through the React workspace and typed FastAPI API. Summarizer, Generator and Assistant remain navigation groups, not separate applications. See [free access](free-access.md) for the current hosted/local profiles and [architecture](architecture.md) for transport and storage.

## Inputs and outputs

| Route | Input | Processing and output |
| --- | --- | --- |
| `text-summary` | Pasted text | Readable summary. |
| `youtube-summary` | YouTube URL or pasted transcript | Transcript extraction/recovery, then summary. |
| `article-summary` | Public article URL | Readable article extraction, then summary. |
| `file-summary` | One PDF/DOCX | File extraction, then summary. |
| `ocr` | One PNG/JPG/JPEG | Tesseract text extraction; optional separate summary action. |
| `image` | Prompt | Generated image and actual provider/artifact metadata. |
| `speech` | Text and mode-specific voice | Audio artifact with explicit playback. |
| `captions` | YouTube URL or pasted transcript | Readable transcript; no fabricated timestamps. |
| `code` | Task and Python/JavaScript/Java/C/C++ | Initial code, actual available checks, at most one repair, final code/checks. |
| `content` | Idea, tone, platforms, optional narration and voice | Plan, script, image prompts, captions, hashtags, CTA, review, narration or its error. |
| `research` | Topic and up to five supplied URLs | Plan, source digests, cited report, critique, conditional revision, citation-label checks and partial-source errors. |
| `documents` | Up to three PDF/DOCX/TXT/images | Per-file summary, classification, entities, action items, risks and file errors. |
| `document-qa` | Up to three PDF/DOCX, then a question | Explicit extraction/indexing followed by retrieval, answer and source inspection. |
| `url-qa` | Up to three supplied URLs, then a question | Explicit extraction/indexing followed by retrieval, answer and source inspection. |
| `support` | Question and up to five support URLs | Intent/severity, response, confidence, citations, Answer/Escalate decision and next step. |

## Mode differences

Free access uses the configured hosted profiles and server utilities; visitors supply no key. Local text uses the smaller CPU model. Advanced mode requires an explicit visitor OpenAI key. Image generation needs hosted capacity. Free speech offers Heart, Bella, Nicole, Michael, Fenrir and Emma; advanced speech retains alloy, echo, fable, onyx, nova and shimmer.

Free/local inputs are bounded to 12,000 BGE tokens per source/file and 50 PDF pages, with explicit rejection rather than silent truncation. Summaries process all admitted sections. Retrieval uses 384-token chunks with 64-token overlap and combines semantic and keyword candidates to return four chunks. Additional prompt/context limits are in [free access](free-access.md).

Advanced mode preserves these workflow settings:

| Workflow | OpenAI / local utility settings |
| --- | --- |
| Text summary | `gpt-3.5-turbo`, output cap 300; no-key utility fallback uses DistilBART min 100/max 300. |
| URL/video/file summary | DistilBART min 100/max 300, deterministic inference, first 4,000 extracted characters. |
| Images | `gpt-image-1`, one 1024×1024 image. |
| Speech | `tts-1`, six OpenAI voices. |
| Code | `gpt-4o-mini`, temperature .2; individual checks have 30-second deadlines; one repair attempt. |
| Content | `gpt-4o-mini`, temperature .4; existing five tones and five platforms. |
| Research | `gpt-4o-mini`, JSON temperature .2/text .3; up to 12,000 characters per source. |
| Documents | `gpt-4o-mini`, temperature .2; up to 14,000 characters and existing JSON heuristics. |
| Document Q&A | OpenAI embeddings, chunks 1,200/overlap 180, top four; `gpt-4o-mini`, temperature .2. |
| Article Q&A | OpenAI embeddings, chunks 1,000/overlap 160, top four; same answering profile. |
| Support | `gpt-4o-mini`, temperature .2; up to 10,000 source characters; human-required, low-confidence, missing/unknown-citation or draft-escalation paths escalate. |

The no-context runtime path remains useful for unit tests and explicit SDK-backed calls; it is not an additional interface. `backend/tests/test_parity.py` compares over sixty workflow-function AST hashes with committed fixtures and exercises branch behavior. Removing obsolete presentation code does not change those functions.

## Result semantics

Passed code checks mean syntax/compilation only. Confidence and model review are reported model outputs, not independent verification. Free-mode schema/source failures cannot silently become a passed review. Some advanced paths retain heuristic/fallback behavior; its warnings remain visible. Details exposes complete structured output.

Forms remain inspectable before credentials or a live session exist. Inputs survive failures and in-tab navigation. Q&A requires explicit preparation and reprocessing when relevant inputs or mode change. Samples are separately labelled fixtures, never uploaded files or substitutes for a failed request.
