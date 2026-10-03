# Free-access verification (quality acceptance pending)

The free-access extension has **113 passing backend tests and eight passing frontend tests**. Production build/type checks passed. All fifteen adapters are exercised without visitor credentials using mocked hosted providers, real parsers/index persistence, and actual syntax/compiler checks. Tests cover quotas/reservations, HMAC network limits, UTC resets, explicit routing, format repair, requested caption platforms, complete word/Unicode section coverage, unavailable reviews, specific document failure diagnostics, pinned model checks, and Turnstile hostname/action validation.

The owner selected stronger outputs over more daily runs. The current hosted text profile is **Llama 3.3 70B**, with its higher published compute rates used for reservations. A real browser summary completed in four seconds without a visitor key and identified the actual provider/model in Details. Ten hosted benchmark summaries completed before the application's conservative daily hosted allowance paused the next case. Two long summaries exposed clipped-word artifacts; section boundaries now retain available whole words. These cases and the remaining benchmark require a fresh final-profile evaluation. Do not attribute the earlier Qwen benchmark to Llama.

The earlier real **Qwen hosted** 60-case baseline completed without workflow errors or local fallback: 85/88 expected facts appeared in outputs, 10/10 absent-answer questions were declined, 6/6 code outputs passed existing syntax/compiler checks, and 4/4 required support cases escalated. **Grounding acceptance failed** because marketing copy invented product details and confused quantities/dimensions. Fact presence is a screening metric, not an accuracy percentage.

The **local CPU** staged evaluation now has successful outputs for all 60 cases, including explicit reruns after failures: 85/88 expected facts, 10/10 missing-answer refusals, 6/6 syntax/compiler checks and 4/4 required escalations. It is not one uninterrupted run of the final code. **Local grounding acceptance remains failed:** creative copy sometimes converted a project budget into a unit price, omitted key details or added unsupported claims; research sometimes treated missing documentation as proof that a method did not exist. Failed/unavailable review results stay visible. The final 18-case support/code/content batch completed with no execution errors after local model/cache unloading was enabled, and the previously failed document case succeeded in 93.6 seconds. Six research cases took 293–492 seconds on two CPU threads. Earlier resident-cache runs exhausted memory even at an 8 GB limit; `keep_alive=0` releases each generation's cache. Target-VM peak memory and latency remain unverified.

A real 1024 × 1024 FLUX image was visually inspected. Six pinned Kokoro MP3 previews were generated and decoded; browser playback, switching, focus return and a real keyless speech request were checked. New controls were inspected at 360/768/1024/1440/1920 px without page overflow. This does not establish subjective voice quality or a universal accuracy guarantee. Native ARM/AMD CI exercises real pinned embeddings/index recovery, decoded speech, constrained local inference and cache unloading; check the latest commit's PR checks before acceptance.

Raw synthetic outputs, provenance, screening metrics and remaining gates are in [evaluation evidence](evaluation/README.md). No production publishing, account provisioning, purchases or paid OpenAI tests have occurred. The full final-profile hosted grounding benchmark, subjective media review, target-VM capacity, deployed field performance and public anti-abuse configuration remain acceptance gates.

![Real keyless Llama summary in the browser](screenshots/free-live-summary.png)

The rest of this file records the original React migration validation.

# Verification record

Implementation branch: `codex/trace-react-workspace`. Baseline: `17cc2b65b700ef2312d80fdaa62127e943dc61cb`.

## Completed locally

- Production Next.js build and strict TypeScript check.
- Six frontend tests: typed requests for all fifteen tools, creative options, chunk boundaries, observed stages, terminal errors, interruption without replay, and the five local sample fixtures.
- 72 Python tests: original function/prompt parity snapshots, all fifteen adapters with mocked providers, real PDF/DOCX/TXT/PNG/JPG/JPEG upload parsing through the API, research revision and partial sources, missing/unknown citation labels, support escalation rules, heuristic document fallback, the single repair attempt, compiler absence, actual five-language checks, OCR, FAISS/JSON restart recovery, session ownership/clearing/expiry, typed inputs, untruncated text inputs, content-length/chunked request limits, credential warnings and secret redaction.
- Both ARM64 and AMD64 Docker images build with CPU-only PyTorch, FAISS, Tesseract, Node.js, JDK, GCC and G++.
- Real ARM local summary: first download/load/inference took 158.7 seconds in the local check; peak process RSS 1,971,280 KiB (about 1.9 GiB). This is not an Oracle VM latency benchmark.
- Browser inspection at 360, 768, 1024, 1440 and 1920 px: all fifteen empty/ready forms and all five sample output views have no page-level horizontal overflow (100 layout checks). Desktop citation pinning, mobile evidence sheet, light/dark surfaces, command search, keyboard selection, copy feedback and in-tab drafts checked.
- Five samples worked with the backend stopped and no API key. Each remains labeled **Sample result — no live AI request**.
- Mock-provider browser/API integration: a 35-section research report retained a failed source and its observed failed stage; Code Copilot displayed initial failed syntax, one repair and the final separate checks; Document Intelligence accepted a long filename and kept heuristic warnings alongside usable output. Immediate session clearing removed drafts/key/uploads. A backend outage retained text and exposed an explicit retry action.
- Real browser/API integration without a key: local text summarization completed using cached model weights (30 seconds including model load); Tesseract read an uploaded synthetic image. After a backend restart, the same session-owned upload remained available and an explicit retry succeeded. The optional OCR summary action requested a key while preserving extracted text.
- Reduced motion checked with the actual system preference enabled: the media query matched, spatial transforms were absent, and transitions were disabled. The original system preference was restored afterward.
- Rendered Research text contrast sampled on settled surfaces: minimum 5.72:1 in light mode and 7.72:1 in dark mode. Placeholder opacity is 1; control borders/focus indicators use separate high-contrast colors. This is scoped visual verification, not a claim of a complete accessibility certification.

## Interface previews

![TRACE landing page](screenshots/landing-desktop.jpg)

![Research sample with pinned evidence](screenshots/research-desktop.jpg)

![Mobile evidence sheet](screenshots/research-mobile.jpg)

## Architecture-specific limitation

Docker's AMD64 emulation on this ARM Mac does not expose the unprivileged Landlock syscall. Native compiler checks correctly report **unavailable** in that emulation. The earlier unrestricted checks compiled all five languages; the final adapter refuses to bypass isolation. CI uses native Ubuntu x86 and ARM runners and requires isolation support, so emulation cannot silently substitute for native validation.

## Remaining acceptance checks

No test OpenAI key was supplied, so no paid live-provider requests have been made. Mocked-provider parity is not a claim of live parity. A controlled key-enabled test should cover the actual report review/revision flow, embeddings/Q&A and small agreed image/audio requests before final live acceptance.

Field LCP/CLS/INP require a deployed site and representative traffic. Local responsive/build checks do not establish field performance. Deployment, production promotion, Oracle provisioning and accounts are intentionally deferred.

GitHub Actions validates clean Linux dependency installation, production frontend build/types/tests and native ARM64/AMD64 backend containers. Both native jobs require compiler isolation and check CPU-only tensor capability. The latest outcomes are available on [the pull request](https://github.com/Archit-k20/Agentic-Workflows-GenAI-/pull/1/checks).
