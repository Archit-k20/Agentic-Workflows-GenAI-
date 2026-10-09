> The free-access extension adds explicit provider modes, local hybrid retrieval/speech, persisted fair-use limits and public Turnstile verification. See [the current free-access architecture](free-access.md). The original migration architecture below remains the OpenAI parity reference.

# TRACE implementation

## Layout

- `frontend/`: Next.js 16.3.8, React 19.3.0, TypeScript, Tailwind 4, Radix UI, Motion, Lucide, locally served font files. Vercel project root is this directory.
- `workflows/`: shared Python business functions extracted from the baseline. Streamlit and FastAPI call the same prompts and processing functions.
- `backend/`: Python 3.11 FastAPI transport, SQLite/file storage, workflow observations, safe URL fetching, and compiler filesystem guard.
- `backend/openapi.json` and `frontend/src/lib/api-types.ts`: committed API schema and generated types. Regenerate when contracts change.
- `docs/feature-parity.md`: the fifteen contracts and infrastructure changes.

## Data flow

Browser drafts, results, API key, and anonymous token remain in memory. Only the light/dark preference uses localStorage. Samples are bundled synthetic results and bypass all networking. Live execution creates a lazy anonymous session, uploads files directly to the Python service, and consumes request-bound SSE events with fetch. Browser interruption never replays a request. The service has two execution slots and one serialized local-model instance.

A stage is emitted when its function actually starts and when it completes or fails. There are no estimated percentages or model-token streams. JSON/provider fallbacks are warnings. The frontend exposes every retained result field in Details. A model review is a reported model outcome; citation checking checks labels; compilation checks do not prove correctness or security.

## Temporary storage and ownership

`Storage` defines a small adapter boundary. `LocalStorage` stores hashed session tokens and expiring metadata in SQLite. A private mounted directory contains session-owned uploads, artifacts, and contexts. Indexes use `faiss.write_index` plus JSON text/metadata, never uploaded pickle or LangChain pickle persistence. Access expires before 24 hours; housekeeping runs every minute inside that retention bound. Clearing deletes the session and all its files. Browser queries after expiry instruct users to reprocess.

API keys are request headers and local variables, never storage fields. Uvicorn access logging is disabled in the container. Artifact fetches use an Authorization header and authenticated blob URLs in the browser; session tokens are not URL parameters. CORS uses exact origins. JSON requests are bounded; each supported upload accepts at most 200 MB. Source fetching pins a resolved public IP, validates every redirect, limits response bytes, and enforces socket/deadline timeouts.

Native compiler child processes run in their own source directory with unprivileged Linux Landlock rules that exclude session data. Python uses parsing/bytecode compilation only. Generated programs are never executed. If Landlock is unavailable, native checks return unavailable rather than dropping the restriction. Docker cross-architecture emulation does not expose Landlock; native CI covers both architectures. This restriction protects session files; it is not a general code security assessment.

## Operation boundaries

No users/accounts, permanent history, background queue, cancellation, autonomous web search, publishing, new exports, or token streaming. A blocking provider request cannot be forcibly cancelled; after disconnect, the next observed stage stops, and the execution slot is released when the current call unwinds. No automatic generation retry is added by the transport. Existing OpenAI SDK retry behavior remains unchanged.

Local storage is suitable for one mounted Oracle VM. A later Cloud Run deployment needs a shared storage implementation and distributed concurrency management rather than ephemeral files or per-instance slot assumptions. Deployment is intentionally deferred.
