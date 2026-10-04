# Llama quality assessment — 4 October 2026 IST

**The complete hosted suite ran successfully, but output-quality acceptance failed.** All 60 cases completed without execution errors or local text fallback: 54 used Llama 3.3 70B and six code tasks used the pinned Qwen Coder model. All 60 transport schemas validated. Screened fact presence was 87/88 (98.86%), missing-answer refusals 10/10, syntax/compiler checks 6/6 across five languages, and required escalations 4/4. Fact presence is not accuracy; syntax/compilation is not a behavior or security proof.

| Area      | Actual finding                                                                                                                                                                                                                                        | Required correction                                                                                                                                                    |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Research  | All six reviewed final reports lost citations and the five required headings, although drafts had them. Some reviews also assert source unreliability without evidence.                                                                               | Validate each revision and preserve the last structurally valid draft with truthful review status. Distinguish untrusted instructions from factual source credibility. |
| Support   | Both supported, low-risk requests escalated for missing citations. Returning within 20 days under a 30-day unopened-item policy was incorrectly rejected, and that answer remains visible. Three source digests import allegations from the question. | Separate question allegations from documentation, enforce citation coverage, test numerical policy boundaries, and avoid presenting rejected drafts as guidance.       |
| Content   | Model critiques pass all six packages, but some copy invents a contact role, a latest initiative or an early-adopter/exclusive audience. Some scripts drop budget/refund conditions.                                                                  | Validate claims and material facts separately from creative proposals; do not trust model self-review as factual certification.                                        |
| Documents | One analysis omits the screened 32-kit quantity; another assigns shipping to the owner without an explicit task assignment.                                                                                                                           | Preserve material quantities and leave unknown assignees unspecified.                                                                                                  |

The prior clipped-word summary and budget-as-unit-price defects were not seen in these final-profile fixtures. Summaries and Q&A were the strongest areas in this run. A real anonymous HTTP summary returned in 2.57 s; a real synthetic PDF was uploaded/indexed in 0.96 s and answered with a citation in 0.93 s. A second session could not access that context, and test sessions were cleared. Document Q&A retains its PDF/DOCX input support. Warm local timings do not establish public latency.

The backend suite passed **118 tests**, including session ownership, expiry, index recovery, processing branches, quotas and real isolated compiler checks. The editorial commit's frontend build/types/eight tests and native ARM64/AMD64 pipeline checks are all green. No frontend changes were made in this testing pass. Only evaluation/reporting code changed: explicit priority ordering retains all remaining fixtures, and the report now catches missing citations/sections and unnecessary supported-request escalations. No prompts, providers, models or application workflow behavior were changed to conceal failed outputs.

The full raw outputs, metrics, individual source-based findings and HTTP evidence are in [evaluation evidence](evaluation/README.md). The test report's inference fingerprint matches current repository code. This run stayed within the existing shared application allowance; no paid requests, quota resets, deployment or merge occurred. Public Turnstile/proxy/origin setup, varied real-source/adversarial evaluation, optional paid-provider live parity, subjective media review, target-VM capacity and deployed field performance remain later acceptance work. No new credentials or manual account steps are required to address the quality defects locally.

# Editorial workshop UI — 4 October 2026

The owner selected warm paper surfaces, ink typography and a vermilion accent. This pass replaces the cool dashboard treatment with a light-by-default editorial workshop, while retaining saved theme preferences and a warm charcoal dark theme. Newsreader now establishes the landing/workspace hierarchy; Manrope remains the interface face and IBM Plex Mono labels technical metadata. Fonts remain self-hosted.

The workspace now separates the input desk from the output sheet, uses indexed navigation and document corner marks, and treats pinned evidence as marginal annotations. Code retains a charcoal reading surface with a lined verification console; content artifacts use a responsive workbench grid; document entities use ruled indexes; support decisions retain their actual answer/escalate state. No provider, prompt, retrieval, verification or quota behavior changed. All fifteen forms and structured Details remain available.

Validation of this pass:

- Production build, TypeScript check, eight frontend tests, formatting and diff checks passed.
- Browser layout inspection across the landing page and all fifteen tools at 360, 768, 1024, 1440 and 1920 px in both themes: 160 checks, no page-level horizontal overflow. The five sample output views were included.
- Rendered Research text contrast sampled on settled surfaces including navigation, controls, labels, reports, sample notices and the pinned inspector: 47 samples per theme, minimum 5.13:1 light and 6.04:1 dark. This is scoped verification, not complete accessibility certification.
- Keyboard command search opened Code Copilot; desktop citation pinning and mobile evidence sheet worked. Escape dismissed the mobile evidence sheet and settings drawer. The free/local/advanced mode choices remained available in mobile settings.
- Final production preview served at localhost:3000. The screenshots below show the actual application, not a concept mockup.

Existing reduced-motion handling is preserved; the prior OS-level check below was not repeated in this pass. No live AI requests were made, and final-profile output-quality evaluation remains deferred until the shared allowance resets. No deployment or merge occurred.

![Editorial workshop public entry](screenshots/editorial-landing-desktop.jpg)

![Editorial Research workspace with pinned source](screenshots/editorial-research-desktop.jpg)

![Editorial mobile evidence inspector](screenshots/editorial-research-mobile.jpg)

# Earlier free-access verification (historical record)

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
