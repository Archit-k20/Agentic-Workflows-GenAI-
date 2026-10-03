# Model evaluation evidence — 3 October 2026 UTC

All cases use committed synthetic English source text. Provider/model inference is real; synthetic URL text is supplied by the evaluation harness, so these runs do not test extraction from live websites. No paid OpenAI calls were made. Screening metrics count facts in outputs only, weight by expected fact count, and give missing/error cases zero. **96.59% fact presence is not 96.59% accuracy.** Grounding/usefulness review is a separate gate.

| Evidence | Scope | Outcome / limitation |
| --- | --- | --- |
| `hosted-grounded.json` / `hosted-qwen-metrics.json` | Earlier Qwen3 30B hosted baseline, 60 cases | No execution errors/fallback; 85/88 facts, 10/10 refusals, 6/6 syntax checks, 4/4 required escalations. Grounding failed: invented marketing claims and dimensional interpretation of a shipment count. |
| `hosted-content-bounded.json` | Six shorter-content Qwen reruns | Output completed, but unsupported claims remained. Not current Llama results. |
| `candidate-70b-one-case.json` | One Llama 3.3 70B content comparison | Better source adherence in this example; not enough evidence for a general quality claim. |
| `hosted-70b-progress.json` | Ten successful Llama summaries, followed by a quota error on summary 11 | Hosted-only, no local substitution. Application budget stopped the run. Long section word-fragment artifacts were fixed afterward; these must be retested. Full current-profile gate pending. |
| `local-staged.json` / `local-staged-metrics.json` | Latest recorded local output per case across staged runs and fixes | 60 successful outputs after reruns; 85/88 facts, 10/10 refusals, 6/6 syntax checks, 4/4 escalations. Not a single uninterrupted final-code benchmark. Grounding failed. |

## Provenance and failures

The local row's `provenance_run` identifies its original run. First runs used earlier prompts/JSON guidance; document/research reruns used decoder-level schemas. The final `local-unload-rest` run covered all six support, six code and six content cases with cache unloading enabled, completing all 18 without execution errors. `local-doc07-unload` explicitly reran the earlier failed document case successfully. Earlier local document failures included `documents-03` (format), `documents-07` (memory exhaustion); resident-cache stress runs exhausted both 6 GB and 8 GB limits. Increasing the memory limit alone was insufficient. The final profile unloads after each generation.

Concrete local grounding failures remain visible in the saved outputs: `content-01` describes the USD 740 budget as a per-kit price; `content-06` describes USD 330 as a per-unit price and invents technology claims; `content-04` omits important shipment/owner details in its script. Research outputs sometimes equate undocumented methods with methods never performed and identify a project owner as a recipient. Model reviews can flag issues yet leave factual mistakes in the final revision. None of these are declared a grounding pass. Accepted syntax checks certify syntax/compilation only.

Hosted Qwen creative-copy review similarly failed even when schemas and expected-fact screening passed. The owner explicitly chose the larger Llama model to prioritize quality over daily capacity. Its full grounding evaluation is still pending. Raw `rubric_review` null fields are deliberate: do not interpret unreviewed rows as passed rubric scores.

## Next evaluation after the UTC reset

The application resets at **00:00 UTC (05:30 IST)**. The prior progress file predates the section fix; use a fresh output file for the final profile. Inside the configured backend container (owner credentials already injected):

```sh
python -m backend.evaluation.run --mode free --hosted-only --stop-on-error --output /data/evaluation/hosted-70b-final.json
```

If it stops on the daily application budget, explicitly run the same command with `--resume` after a subsequent UTC reset. It preserves successful rows and retries errors/missing cases only when instructed. Resume validates model names, local digest and inference-code fingerprint; changed processing requires a new file. There is no scheduled or automatic replay. A 60-case larger-model benchmark may span several daily budgets; do not bypass the budget or enable paid overflow.

Use `python -m backend.evaluation.report /data/evaluation/hosted-70b-final.json` for screening metrics, then review actual claims against `backend/evaluation/cases.json`. Grounding, useful outputs, preserved material details, source conflicts and missing-answer behavior must pass separately. Inspect image output and listen to all voices before final media acceptance. Deployment capacity must be measured on the proposed VM; these Mac/Docker timings do not prove Oracle performance.
