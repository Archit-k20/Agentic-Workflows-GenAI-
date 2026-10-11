# TRACE architecture

TRACE has a Next.js frontend, a Python FastAPI service and a private Ollama sidecar. The frontend runs on Vercel; the API, CPU tools and temporary storage run on a Google Compute Engine VM. See [deployment](deployment.md) for the operating configuration and [verification](verification.md) for the limits of the available evidence.

## Repository boundaries

- `frontend/`: Next.js 16.3.8, React 19.3.0, TypeScript, Tailwind, Radix primitives, Motion, Lucide and self-hosted fonts.
- `backend/`: Python 3.11 transport, typed contracts, provider adapters, public-use controls, retrieval, storage and tests.
- `workflows/`: tool processing functions and the preserved OpenAI prompts/review rules. They have no UI-framework dependency.
- `huggingface/image-fallback/`: the private Gradio FLUX worker. It performs image inference only.
- `backend/openapi.json` and `frontend/src/lib/api-types.ts`: committed OpenAPI schema and generated frontend types.
- `compose.yaml`: API, private Ollama, persistent volumes and the pinned-model installer.

## Frontend and samples

`/` introduces the project. `/explore` holds the collection and five interactive synthetic examples. `/workspace` opens Research Agent; `/workspace/[tool]` supports direct links to all fifteen tools. `?sample=1` selects a read-only fixture.

The root provider holds live inputs, files, results, contexts, execution mode, API key and anonymous token in memory. Only the theme uses localStorage. Samples use a separate fixture state and never overwrite live drafts or replay a request. Collection examples do not mount the execution controller or visitor verification. Samples remain usable without the backend.

Presentation is separated into navigation, input controls, settings, result surfaces and `useToolController`. `ToolPresentation` maps tool IDs to presentation families, builder notes and sample availability. The [interface guide](interface.md) describes the current UI. Live media uses authenticated fetches and cleaned-up object URLs.

## Request and provider flow

A live action lazily creates an anonymous session, uploads files to the API when needed, and consumes request-bound workflow events using `fetch`. Events include `started`, `stage`, `warning`, `result` and `error`. Stages reflect observed execution; they are not model reasoning traces or token streams. An interrupted request is never automatically replayed.

Free mode uses Cloudflare Llama for text and Qwen Coder for code. OCR, extraction, embeddings, hybrid retrieval and Kokoro speech run on the server. An unfinished text stage may continue on the pinned Ollama CPU model, with later text stages remaining local for that run. Image fallback is narrower: an explicit Cloudflare capacity rejection may submit once to the configured private Hugging Face worker. Ambiguous image failures require an explicit retry.

Local mode uses the backend CPU model and still fetches submitted URLs. It does not provide local image generation. Advanced mode explicitly selects the visitor's OpenAI key and existing OpenAI workflow behavior. See [free access](free-access.md), [image routing](huggingface-images.md) and [tool contracts](tools.md).

## Retrieval and tool checks

Free/local Q&A uses normalized BGE embeddings, FAISS semantic candidates and BM25 keyword candidates, combined with reciprocal-rank fusion. It returns four chunks with their actual text and metadata. Contexts record the embedding profile and require reprocessing if that profile changes. The advanced path retains its OpenAI embeddings and retrieval parameters.

Code checks use Python AST/bytecode compilation, Node syntax checks, javac and GCC/G++ syntax checks. Generated programs are never executed. Native compiler child processes use unprivileged Linux Landlock restrictions that exclude session data. If those restrictions are unavailable, native checks report unavailable. A successful check does not establish functional correctness or security.

Source checks and model reviews are bounded and fallible. A citation-label check verifies labels, not the truth of the cited claim. Rejected revisions, unavailable checks and partial failures remain available in the result.

## Storage and security

`Storage` is a small adapter interface. `LocalStorage` uses SQLite for hashed session-token metadata and private mounted files for uploads, artifacts and contexts. Session data expires within 24 hours; housekeeping runs every minute. Session clearing deletes the current session's temporary data. Ownership is checked for contexts and artifacts.

Server-created indexes use FAISS plus JSON metadata. Uploaded pickle files are not deserialized. Contexts survive an API restart while their session remains valid, but closing/reloading the browser loses its in-memory token and drafts.

Provider secrets remain on the backend. Visitor OpenAI keys remain in browser/request memory and are not storage fields. Artifacts use an Authorization header, not token-bearing URLs. Uvicorn access logging is disabled in the container. Exact CORS origins, Turnstile validation, upload/request limits and persisted fair-use controls protect public execution. Each supported file can be at most 200 MB; tool-specific token/page limits also apply.

Source fetching resolves and pins public IPs, checks every redirect, limits response sizes and uses bounded deadlines. The reverse proxy overwrites untrusted forwarding headers, and the backend trusts only the configured proxy peer.

## Resource boundaries

One API process admits at most two workflows. Local text, embeddings and speech share a CPU gate; two admitted workflows do not imply parallel local-model inference. The Ollama model/cache unloads after each generation (`keep_alive=0`) to avoid accumulated prompt-cache memory, at the cost of reload latency.

SQLite and mounted files fit the current single-VM deployment. A multi-instance or ephemeral-host deployment would need shared storage and distributed concurrency controls. No background-job system, accounts, permanent history, autonomous web search, cancellation, new export formats or publishing integration is implemented.
