# Verification record

Implementation branch: `codex/trace-react-workspace`. Baseline: `17cc2b65b700ef2312d80fdaa62127e943dc61cb`.

## Completed locally

- Production Next.js build and strict TypeScript check.
- Frontend transport tests: chunk boundaries, observed stages, terminal errors, interruption without replay, and five local sample fixtures.
- Python suite: original function/prompt parity snapshots, all fifteen adapters with mocked providers, research revision and partial sources, missing/unknown citation labels, support escalation rules, heuristic document fallback, the single repair attempt, compiler absence, actual five-language checks on ARM, OCR, FAISS/JSON restart recovery, session ownership/clearing/expiry, typed inputs, request limits, and secret redaction.
- Both ARM64 and AMD64 Docker images build with CPU-only PyTorch, FAISS, Tesseract, Node.js, JDK, GCC and G++.
- Real ARM local summary: first download/load/inference took 158.7 seconds in the local check; peak process RSS 1,971,280 KiB (about 1.9 GiB). This is not an Oracle VM latency benchmark.
- Browser inspection at 360, 768, 1024, 1440 and 1920 px: no page-level horizontal overflow in the research view. Desktop citation pinning and mobile evidence sheet, light/dark surfaces, command search, keyboard selection, and in-tab navigation checked.

## Architecture-specific limitation

Docker's AMD64 emulation on this ARM Mac does not expose the unprivileged Landlock syscall. Native compiler checks correctly report **unavailable** in that emulation. The earlier unrestricted checks compiled all five languages; the final adapter refuses to bypass isolation. CI uses native Ubuntu x86 and ARM runners and requires isolation support, so emulation cannot silently substitute for native validation.

## Remaining acceptance checks

No test OpenAI key was supplied, so no paid live-provider requests have been made. Mocked-provider parity is not a claim of live parity. A controlled key-enabled test should cover the actual report review/revision flow, embeddings/Q&A and small agreed image/audio requests before final live acceptance.

Field LCP/CLS/INP require a deployed site and representative traffic. Local responsive/build checks do not establish field performance. Deployment, production promotion, Oracle provisioning and accounts are intentionally deferred.

Final native CI outcomes, offline sample/contrast evidence and UI screenshots are recorded in the pull request and updated here after verification.
