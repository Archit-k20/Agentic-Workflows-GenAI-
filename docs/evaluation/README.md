# Interview launch checks — 9 October 2026

[Full raw hosted run](hosted-launch-final-2026-10-09.json): 60 cases, no execution errors or local fallback. [Source-based review](launch-review-2026-10-09.json) records the remaining quality issues; this is **not** a passing release-quality gate. All sixteen Q&A outputs retained supported answers or refused absent evidence. Support omitted a documented shipment from its excerpt and unnecessarily escalated; missing guarantee evidence was sometimes phrased as actual absence. Follow-up code retains missing numerical support sentences and makes unknown-evidence instructions explicit, without changing original OpenAI workflow functions.

The first hosted follow-up was refused as unavailable/free allowance exhausted; no repeated retry or quota reset. Changed inference profiles need fresh evidence, not renamed earlier passes. The earlier Mac local retest still exposed unsupported arrival wording; new source guards are deployed and VM targets completed in 621.92/552.92 seconds. The targeted date/evidence errors improved, but source review still found omitted owners, duplicate refund wording and overconfident review comments; full local quality remains unaccepted. See [VM review](vm-local-launch-review-2026-10-09.json). Target-server/public-browser acceptance are separate. The pinned installer passed a real fresh-volume download and inference smoke test. Vercel and the Google trial VM are now live. Public wiring, browser speech/fallback, samples and selected native/state checks passed; full quality/interview acceptance remains incomplete. See [the dated launch record](../launch-2026-10-09.md).

---

# Current launch evidence — 8 October 2026 IST

**Launch acceptance remains incomplete.** Read [verification](../verification.md) and [launch-review-2026-10-08.json](launch-review-2026-10-08.json) for current changes, provenance, source-based findings and remaining gates. Older sections below record earlier profiles and their failures.

| Evidence | What it establishes | Limit |
| --- | --- | --- |
| `availability-2026-10-08.json` | One bounded Llama request returned HTTP 200/READY | Does not diagnose the earlier mismatch or guarantee continuing allowance |
| `hosted-boundaries-2026-10-08.json` and metrics | Seven boundary cases; expected routing/assignee/material details retained | Earlier d323 profile; diagnostic model fields can still be wrong |
| `hosted-final-2026-10-08.json` and metrics | 60/60 completed, no fallback/errors; 88/88 fact presence, 10 refusals, six syntax checks, four required escalations, two supported answers | Historical d323 profile despite filename; source-quality acceptance failed |
| `hosted-launch-corrected-2026-10-08.json` | Six completed intermediate cases, seventh stopped by the application reservation ceiling | 5eb0 profile; quality still failed; not final-profile acceptance |
| `local-launch-targets-final-2026-10-08.json`, metrics and two-case fixture file | Real final-profile Qwen 4B content execution, 353.15/234.19 seconds, 4/4 facts | Source-quality failed; narrow cohort and slow CPU fallback |
| `real-url-extraction-check-2026-10-08.json` | Actual official Python URL extracted readable nonempty text after compression fix | Extraction only, no AI; raw copyrighted text excluded |
| `launch-review-2026-10-08.json` | Separate source-based findings, hashes, profile differences and pending checks | Finite guards and synthetic fixtures do not certify general accuracy |

Historical 8 October check: 192 backend tests and eight frontend tests/types/build passed before public hosting. Current deployed source passes 217 backend tests and green native ARM64/AMD64/frontend CI; see the newer launch record above.

After the next deliberate allowance check, use a **new filename** for the current hosted profile, prioritize the affected cases, then include all remaining fixtures:

```sh
python -m backend.evaluation.run --mode free --hosted-only --stop-on-error \
  --priority content-05 content-03 research-05 support-01 support-02 documents-08 \
  --output /data/evaluation/hosted-launch-final-new.json
python -m backend.evaluation.report /data/evaluation/hosted-launch-final-new.json
```

Only resume deliberately with an unchanged fingerprint. The application allowance resets at 00:00 UTC (05:30 IST); availability is not guaranteed by the reset. Preserve prior results, failures and the ledger. No paid overflow or quota bypass.

---

Historical records:

## Dashboard evidence follow-up

The owner's screenshot shows 5.56k/10k today, contradicting the quota-exhausted API message. A single fresh bounded probe still returned HTTP 429/code 4006. Treat this as an unresolved enforcement/reporting mismatch, not a confirmed 10k daily consumption. `dashboard-quota-recheck.json` records the two distinct dashboard periods and diagnostic IDs. The owner confirmed the dashboard/API account match. Documented UTC reset is not a guarantee that this inconsistency resolves; deliberately check availability before a new benchmark. Core correction commit 5073a65 passed frontend and both native architecture CI jobs; the frontend is unchanged.

# Current source-check correction status — 4 October 2026 IST

See [verification record](../verification.md) for the implemented guards, tests and remaining gates. **The final-profile full hosted suite is pending**, after Cloudflare explicitly exhausted its account-wide free allowance. The prior sixty-case run below establishes the failures before these corrections; its fingerprint no longer describes the current adapter.

New evidence:

- `hosted-boundaries-first-pass.json`: seven completed Llama cases on the earlier correction profile. Day 20/30/31, conflicting-policy escalation and explicit document assignment worked; receipt routing exposed a guard false positive, subsequently corrected. `...-metrics.json` uses the latest accepted-output screen; raw original scores remain intact. This is not final-code quality acceptance.
- `hosted-boundaries-capacity-stop.json`: Hosted attempt stopped by provider capacity on its first case, with no successful complete cases. The final denial-wording check changed the fingerprint afterward; use the new retest filename after reset.
- `cloudflare-capacity-check.json`: HTTP 429 / error 4006 explicitly reports the daily 10,000-Neuron allocation exhausted. Estimated application text reservations 6,095.81; not actual provider usage. No paid upgrade or quota reset.
- `local-assignment-sourcechecked.json` and metrics: one real current-profile CPU document case, correct explicit assignee/evidence, material details retained, unknown priority, 123.85 s; cache unloaded. Not a full local benchmark.
- `source-checks-review.json`: source-based findings, fingerprints, evidence hashes, guard limitations and remaining tests.

161 backend tests, eight frontend tests/typecheck and real CPU embedding/index/speech smoke checks pass. Source guards do not certify arbitrary factual correctness. The final-commit native checks and future target-VM/live quality acceptance remain separate.

---

## Hosted baseline before source-check corrections

# Model evaluation evidence — updated 4 October 2026 IST

All cases use committed synthetic English source text. Provider/model inference is real; synthetic URL text is supplied by the evaluation harness, so these runs do not test extraction from live websites. No paid OpenAI calls were made. Screening metrics count facts in outputs only, weight by expected fact count, and give missing/error cases zero. **96.59% fact presence is not 96.59% accuracy.** Grounding/usefulness review is a separate gate.

The final Llama-profile suite completed **60/60 cases with no execution errors or local text fallback** on 4 October. It contains 54 Llama text cases and six Qwen Coder cases. **Quality acceptance failed** despite 87/88 screened facts: every Research revision lost citations/sections, both answerable Support requests escalated unnecessarily, one refund answer was wrong, and some digests/marketing copy remained unsupported. The UI and inference implementation were unchanged during this evaluation.

| Evidence                                                                                   | Scope                                                                   | Outcome / limitation                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hosted-70b-final.json` / `hosted-70b-final-metrics.json` / `hosted-70b-final-review.json` | Current inference fingerprint, one complete hosted-only 60-case run     | 87/88 facts, 10/10 refusals, 6/6 syntax/compiler checks, 4/4 required escalations. No fallback/errors. Grounding/structure failed; both supported Support questions unnecessarily escalated.            |
| `live-llama-summary-smoke.json` / `live-llama-context-smoke.json`                          | Actual anonymous HTTP API, no visitor key                               | Live summary 2.57 s; real PDF upload/BGE indexing 0.96 s and cited Llama answer 0.93 s. Cross-session context access blocked; test sessions cleared. Warm local timings, not field performance.         |
| `hosted-grounded.json` / `hosted-qwen-metrics.json`                                        | Earlier Qwen3 30B hosted baseline, 60 cases                             | No execution errors/fallback; 85/88 facts, 10/10 refusals, 6/6 syntax checks, 4/4 required escalations. Grounding failed: invented marketing claims and dimensional interpretation of a shipment count. |
| `hosted-content-bounded.json`                                                              | Six shorter-content Qwen reruns                                         | Output completed, but unsupported claims remained. Not current Llama results.                                                                                                                           |
| `candidate-70b-one-case.json`                                                              | One Llama 3.3 70B content comparison                                    | Better source adherence in this example; not enough evidence for a general quality claim.                                                                                                               |
| `hosted-70b-progress.json`                                                                 | Ten successful Llama summaries, followed by a quota error on summary 11 | Hosted-only, no local substitution. Application budget stopped the run. Long section word-fragment artifacts were fixed afterward; these must be retested. Full current-profile gate pending.           |
| `local-staged.json` / `local-staged-metrics.json`                                          | Latest recorded local output per case across staged runs and fixes      | 60 successful outputs after reruns; 85/88 facts, 10/10 refusals, 6/6 syntax checks, 4/4 escalations. Not a single uninterrupted final-code benchmark. Grounding failed.                                 |

## Provenance and failures

The local row's `provenance_run` identifies its original run. First runs used earlier prompts/JSON guidance; document/research reruns used decoder-level schemas. The final `local-unload-rest` run covered all six support, six code and six content cases with cache unloading enabled, completing all 18 without execution errors. `local-doc07-unload` explicitly reran the earlier failed document case successfully. Earlier local document failures included `documents-03` (format), `documents-07` (memory exhaustion); resident-cache stress runs exhausted both 6 GB and 8 GB limits. Increasing the memory limit alone was insufficient. The final profile unloads after each generation.

Concrete local grounding failures remain visible in the saved outputs: `content-01` describes the USD 740 budget as a per-kit price; `content-06` describes USD 330 as a per-unit price and invents technology claims; `content-04` omits important shipment/owner details in its script. Research outputs sometimes equate undocumented methods with methods never performed and identify a project owner as a recipient. Model reviews can flag issues yet leave factual mistakes in the final revision. None of these are declared a grounding pass. Accepted syntax checks certify syntax/compilation only.

Hosted Qwen creative-copy review similarly failed even when schemas and expected-fact screening passed. The owner explicitly chose the larger Llama model to prioritize quality over daily capacity. Its full current-profile evaluation is now complete and failed the separate grounding/structure gate described above. Raw `rubric_review` null fields are deliberate: do not interpret unreviewed rows as passed rubric scores.

## Current issues and next evaluation

- **Research:** all six final revisions contain no `[S1]`/`[S2]` citations and lose Executive Summary, Findings, Risks and Gaps, Recommended Next Questions and Source List. Drafts contained citations/sections. The final critique's `revised_report` is adopted even when structurally worse. Some critiques also conflate source input that must not be obeyed as instructions with evidence that a source lacks factual credibility. Preserve and validate structure/citations at every revision; retain the last valid draft with explicit failed-review status if a revision degrades it. Do not remove the existing review/revision sequence.
- **Support:** returning an unopened item within 20 days was incorrectly rejected under a 30-day policy. Both low-risk, answerable cases omitted citations and were escalated by the preserved rules. The incorrect draft answer remains in the escalated result. Several digests repeat the customer allegation as source content. Keep question and source facts distinct, validate cited answers and add boundary-reasoning fixtures (20/30/31 days). Missing citations must not count as grounded answers, and invalid drafts must not be presented as accepted guidance.
- **Content:** all six model critiques report a pass, yet the final copy invents a contact role, calls an initiative the owner's latest, or says a pilot is designed for early adopters/exclusive. One playful script drops its budget and refund conditions; another revision removes its budget/refund conditions. Prior budget-to-unit-price mistakes were not seen. Separate proposed creative choices from claims and validate material source facts before accepting copy.
- **Documents:** one analysis omits the expected quantity (the sole screened-fact miss), and another assigns shipment to the project owner without an explicit assignment. Require preservation of material quantities and leave unknown action assignees unspecified.

The report harness now distinguishes unknown citations from entirely missing required citations/sections, checks supported Support routing as well as required escalation, and supports explicit fixture priorities without dropping remaining cases or bypassing the shared budget. Eight report/harness tests and the full **118-test backend suite** pass. Actual generated results were also validated against all sixty transport schemas. Raw `score.rubric_review` fields remain null; completed source-based findings live in the separate review file, rather than relabeling screening metrics as a quality pass.

The run's inference fingerprint matches the repository. The fixture SHA256 and raw-results SHA256 are recorded in the separate review. Local observed memory was 1.564–1.889 GiB for the API and about 57 MiB for idle Ollama; this was not continuous peak sampling. Warm per-case medians: summaries 3.96 s, Q&A 0.96 s, documents 2.88 s, research 38.87 s, support 4.56 s, code 2.46 s and content 13.29 s. The shared text ledger was 4,862.18 Neurons after the benchmark and two successful HTTP live checks, under its 7,000 ceiling; this is the application ledger, not a measured Cloudflare billing total.

No further model requests are needed merely to reproduce these findings. Correct the affected free-mode processing first, then use a **new output file** because the inference fingerprint changes. For a deliberate final-profile rerun inside the configured backend container:

```sh
python -m backend.evaluation.run --mode free --hosted-only --stop-on-error --priority support-01 support-02 research-05 content-05 documents-08 summary-11 --output /data/evaluation/hosted-corrected.json
python -m backend.evaluation.report /data/evaluation/hosted-corrected.json
```

Use `--resume` only after explicitly deciding to retry missing/error cases, and only with an unchanged inference profile. The application resets at 00:00 UTC (05:30 IST). Do not bypass shared limits or enable paid overflow. The current sixty fixtures are synthetic English briefs, not general-purpose quality certification; add varied real-document and adversarial cases before public acceptance. Image/speech implementations were unchanged and their earlier live checks/native smoke evidence remain applicable; subjective media acceptance and target-VM memory/latency still require later validation. No production publishing or paid OpenAI testing occurred.
