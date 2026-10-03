# Free visitor access

Visitors start in **Free access** and enter no API key. All fifteen tool surfaces remain available. Relevant text/image prompts go to Cloudflare Workers AI. OCR, file extraction, embeddings, retrieval and speech run on the backend. If an unfinished text stage cannot use hosted inference, it continues with the smaller local model; later text stages in that run stay local. A warning and execution details identify the change. Image capacity errors preserve the prompt and require an explicit retry.

**Local inference** runs text on the backend's CPU. It still fetches submitted source URLs; it is not an offline browser mode. Image generation requires hosted mode. **Advanced — my OpenAI key** is an explicit option. Typing a key does not select that mode. Visitor keys and mode choices stay in browser memory; only theme preferences persist. Legacy API callers that omit the mode and supply a key retain the original OpenAI routing.

## Owner setup for local development

1. Copy `backend/.env.example` to `backend/.env`. The latter is ignored by Git and Docker builds. Enter the Cloudflare Account ID and a token scoped to this account's Workers AI. Keep the account on Workers **Free**; do not enable paid overflow. Never put owner credentials in a `NEXT_PUBLIC_` variable.
2. Run `docker compose up -d --build`. The pinned Ollama sidecar is private; only the backend's localhost port is exposed. The SQLite/data and model-cache volumes persist across restarts.
3. Run `docker compose exec ollama ollama pull qwen3.5:4b`.
4. Run `docker compose exec backend python -m backend.warmup`. This downloads the pinned BGE/Kokoro assets, checks real embeddings/English speech dependencies, verifies the local model's exact digest and quantization, and performs a short CPU inference. Treat a failure as a setup blocker rather than substituting a different model.
5. In `frontend`, run `npm ci`, then `npm run dev`. The default API URL is `http://localhost:8000`; the UI opens at `http://localhost:3000`.
6. Check `/api/v1/health`: `hosted_configured`, `local_text_ready`, `speech_installed`, and compiler/OCR capabilities. `ready` means the API is serving; configuration flags do not certify Cloudflare credentials, model quality, or warmed model latency.

The six bundled MP3 voice previews work without a backend and make no AI requests. To regenerate them intentionally: `python -m backend.generate_voice_previews --output frontend/public/audio/voices` in the prepared Python environment. Every preview uses the same sentence and pinned Kokoro weights. Playback is explicit, and selecting/closing a voice stops its preview.

## Pinned free profiles

| Task | Engine |
| --- | --- |
| Hosted text | Cloudflare `@cf/meta/llama-3.3-70b-instruct-fp8-fast` |
| Hosted code | Cloudflare `@cf/qwen/qwen2.5-coder-32b-instruct` |
| Hosted images | Cloudflare `@cf/black-forest-labs/flux-1-schnell`, four steps, 1024 × 1024 requested; actual dimensions returned |
| CPU text | Ollama `qwen3.5:4b`, Q4_K_M, digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` |
| Retrieval | `BAAI/bge-small-en-v1.5`, revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`; normalized 384-dimensional CLS vectors |
| Speech | `hexgrad/Kokoro-82M`, revision `f3ff3571791e39611d31c381e3a41a3af07b4987`; six English voices |
| OCR | Tesseract; scanned PDF pages are rasterized and processed individually |

English is the evaluated language. Free voices are Heart, Bella, Nicole, Michael, Fenrir and Emma. The original six OpenAI voices remain in advanced mode. Ollama's server image is pinned by version and image digest in Compose. Python dependency locks install CPU-only torch before packages that depend on it.

## Processing and limits

- At most 12,000 BGE tokens per input/source/file, at most 50 PDF pages, and the original 200 MB allowance per file. Oversize inputs are rejected with a splitting instruction rather than silently truncated.
- Generation stage prompts additionally use conservative UTF-8 byte bounds, reserving 1,024 tokens for templates plus the output cap against 16,384 CPU / 24,000 hosted context limits. Oversize combined prompts ask for fewer sources or shorter input rather than relying on a different tokenizer or upstream truncation. Generation sections contain at most 3,000 UTF-8 bytes, a conservative upper bound on byte-level tokens, with 200-byte overlap; Unicode boundaries are retained. Whole-input summaries process every section before bounded reduction and a 600-token final summary. Generated intermediate summaries have their own reduction bound and cannot loop indefinitely.
- Source digests use 512 output tokens; research text uses 2,400; reports also receive a concision instruction (aim for 350 words), preserving required sections, quantities, citations and conflicts; other generation uses 2,048. Incomplete output is identified. Free mode adds source-grounding/type instructions and permits one structured-format repair. Local structured generation uses decoder-level JSON schemas with nested field types and requested caption platforms; this does not prove factual correctness. It does not change the preserved OpenAI prompts or workflow function bodies.
- Document retrieval uses 384-token chunks with 64-token overlap. Embedding inputs above 512 tokens are rejected. Semantic top 12 and BM25 top 12 are combined using reciprocal-rank fusion with constant 60, returning the top four chunks. Metadata describes actual chunks, not invented page positions.
- Indexes store FAISS and JSON, with an explicit embedding profile. They survive backend restart. Changed/legacy profiles require reprocessing; uploaded files remain available until session expiry. No uploaded pickle is loaded.
- YouTube URL extraction can be blocked by YouTube or lack transcripts. Both YouTube tools accept a pasted transcript as an explicit alternative. No autonomous web search is added.
- Existing code verification and its single repair attempt remain. A passed syntax/compiler check does not establish correctness or security. Failed JSON reviews cannot become a passed review in free mode.
- Workflow requests have a 900-second deadline; hosted calls have at most 120 seconds. Local model inference, embeddings and speech share a CPU gate within the single backend process. Keep one Uvicorn worker; two global workflow slots do not mean two simultaneous local model generations. Compose allows 8 GB for Ollama and 3 GB for the API, leaving 1 GB of the proposed 12 GB VM for its OS. Keeping Ollama resident caused cache-related out-of-memory failures during repeated local evaluation, including at an 8 GB limit. Local calls now use `keep_alive=0`, unloading the model/cache after each generation; files remain cached on disk. This adds reload latency but prevents cross-stage prompt caches from accumulating. Do not treat an increased memory limit alone as the fix. Measure actual combined peak memory on the target VM before deployment.

## Fair use and recovery

SQLite charges each free workflow once for its category: text 20/day, images 2/day, audio 5/day, contexts 3/day. Narrated content reserves both text and audio; unstarted narration is refunded. Pre-compute failures refund their reservation. The same limits apply to the session and an HMAC of its IP, using whichever is exhausted first. Shared networks can share a cap. Clearing a session does not reset the network allowance.

One active workflow per session/network, five starts per minute, and two workflows globally. Counters/reservations survive restart and reset at 00:00 UTC. No raw IP is stored in the usage database. `GET /api/v1/sessions/current/usage` returns remaining allowances and reset time. It is used only after a real request, so local samples do not depend on the backend.

The application reserves conservative compute before hosted calls: 8,000 Neurons/day total with a 7,000 text ceiling, leaving 1,000 for images. Hosted text now uses Llama 3.3 70B after the owner prioritized stronger outputs over more daily runs. Reservations use its published 26,668 input / 204,805 output Neurons per million tokens, rather than the cheaper Qwen profile. This reduces the number of hosted workflows possible per day; the per-visitor allowance does not guarantee account-wide capacity. A 1024-pixel, four-step image reserves 200 Neurons. Known provider usage reconciles reservations; failed/unknown calls keep their conservative reservation. This is an application budget, not a Cloudflare billing cap. The Workers Free plan's enforced allowance is the no-paid boundary. Account-wide usage elsewhere can reduce available capacity.

No generation automatically replays after disconnect, capacity failure or error. Inputs and completed stages remain visible. Explicit retry starts a new request and may consume allowance. Samples are never substituted for a failed live result.

## Before public deployment (later phase)

1. Create a free Turnstile widget in Cloudflare, using the exact frontend hostname, and copy its **site key** to `NEXT_PUBLIC_TURNSTILE_SITE_KEY` in Vercel. This value is public and bundled at frontend build time.
2. Put its **secret key** only in the backend environment. Set `TRACE_PUBLIC_DEPLOYMENT=true` and list the exact allowed widget hostnames in `TRACE_TURNSTILE_HOSTNAMES` (hostnames, without scheme/path). Server verification requires success, an allowed hostname and action `trace-session`; tokens are single-use. Local test mode is not suitable for public operation.
3. Set exact HTTPS origins in `TRACE_ALLOWED_ORIGINS`, the HTTPS backend URL in `NEXT_PUBLIC_API_URL`, and a stable random `TRACE_IP_HASH_SECRET`. Terminate HTTPS with the planned reverse proxy. Set `TRACE_TRUSTED_PROXY_IPS` only to its actual peer addresses, and have the proxy overwrite untrusted forwarding headers. Direct clients cannot select their quota IP via headers.
4. Warm and evaluate the models on the target 2-CPU/12-GB VM. Verify the concurrent memory/latency gates there; Mac/Docker results are not an Oracle capacity guarantee.
5. Confirm quality gates and native ARM64/AMD64 checks before deployment. Vercel publishing, Oracle account/VM provisioning, domains, and production promotion remain deferred.

## Quality evaluation

`backend/evaluation/cases.json` contains 60 synthetic English cases: 12 summaries (including information after the old 4,000-character cutoff), 16 Q&A (10 absent-answer cases), eight document analyses, six research reports, six support decisions, six code tasks covering all five languages, and six content packages. Source fixtures are fixed locally for research/support reasoning tests; the model/provider is real. This does not test live extraction of those synthetic URLs. Parser, network and ownership tests are separate.

Run from the backend container:

```sh
python -m backend.evaluation.run --mode free --owner-env /app/backend/.env --output /data/evaluation/hosted.json
python -m backend.evaluation.run --mode local --output /data/evaluation/local.json
```

Use an environment-injected owner configuration in the deployed container; the `.env` file is not baked into production images. `--owner-env` is optional and is intended for local development. Evaluation also obeys the persisted hosted compute budget, so it can use a large share of that day's free allowance.

Acceptance: hosted fact coverage ≥90%, local ≥80%, absent-answer refusal ≥90%; all accepted outputs have valid schemas and citation labels. Compiler results must reflect actual checks. Review grounding, useful output, preserved numbers/dates/tense, invented owners/deadlines and evidence gaps against the committed facts. Fact-presence scores are a screening metric, not factual-certification scores. A hosted run that falls back locally cannot count as a hosted-only result. Inspect a real image and listen to real speech before media acceptance. Record latency and memory, model versions, failures and reruns; do not silently substitute another model if a gate fails.

Sources: [Cloudflare model catalog](https://developers.cloudflare.com/workers-ai/models/), [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [Turnstile validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/), [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5), [Ollama Qwen 3.5](https://ollama.com/library/qwen3.5).
