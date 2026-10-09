# Private Hugging Face image fallback

TRACE's website remains on Vercel and its main API remains on the Google trial
VM. The extra private Gradio Space runs only image inference. Visitors enter no
new credential and use the existing image form and session-owned artifact route.
This adds an independent limited provider, not unlimited images or a full backend
hosting replacement. Text, code, retrieval, OCR and speech retain their providers.

## Routing and safeguards

1. Cloudflare FLUX remains first choice with the existing prompt/four-step payload.
2. A Cloudflare HTTP 429, or TRACE's exhausted Cloudflare budget before submission,
   can use the private HF worker once. Authentication failures, bad input, ambiguous
   timeouts, other network failures, invalid responses and HTTP 5xx do not trigger
   another image submission. Explicit retry is available after failure.
3. The authenticated Gradio REST adapter checks that the configured Space is
   private, accepts only an HTTPS `*.hf.space` host returned by the official Hub
   API, refuses redirects and never downloads arbitrary returned artifact URLs.
4. The worker returns inline PNG bytes plus a pinned model/revision. TRACE validates
   the four-step profile and actual 1024×1024 PNG before saving the existing
   session-owned artifact. Other visitors cannot fetch the result.
5. HF waits are bounded to approximately three minutes, including its queue;
   network read timeout can add at most 30 seconds. The stream read window exceeds
   Gradio's 15-second queue heartbeat interval. The backend submits once and
   never automatically replays a connection failure. HF may continue an already
   submitted generation after a disconnect; no cancellation feature is claimed.
6. Observable fallback stages, a warning and execution provider metadata identify
   the real engine. No progress percentages or sample substitutions are added.

Existing visitor/network controls remain two image runs per UTC day, one active
workflow per visitor/network, and two concurrent backend workflows. The HF
worker permits one GPU execution at a time and a Gradio queue of four. Its own
provider-wide owner quota is separate from TRACE's per-visitor allowance.

## Owner setup, from the beginning

1. Sign in as the Space owner. On the [official FLUX model page](https://huggingface.co/black-forest-labs/FLUX.1-schnell),
   personally review and accept any model-access conditions. The agent does not
   accept these conditions or disclose contact details on the owner's behalf.
2. At [Access Tokens](https://huggingface.co/settings/tokens), create a dedicated
   `trace-image-runtime` token of type **Read**. A more narrowly scoped fine-grained
   token can instead grant read access to the private Space and gated model.
   Hosted Inference Providers permissions are not required for this own-Space API.
3. Create a second token, `trace-space-deploy`: **Fine-grained → Custom**, selecting
   only the existing `Lamstersickness/trace-image-fallback` repository and granting
   read/write access to its contents/settings. Leave unrelated permissions off.
   The deployment token remains local and must never be a production variable.
4. Save privately in ignored, mode-600 `backend/.env.huggingface`:

   ```dotenv
   TRACE_HF_SPACE_ID=Lamstersickness/trace-image-fallback
   TRACE_HF_API_TOKEN=YOUR_READ_TOKEN
   TRACE_HF_DEPLOY_TOKEN=YOUR_SCOPED_SPACE_WRITE_TOKEN
   ```

   Do not paste tokens into chat, shell arguments, Git, screenshots or the browser's
   TRACE settings. Google/Vercel credentials are not needed in this file.
5. Publish from an environment containing `huggingface_hub`, with the repository as
   working directory:

   ```sh
   python -m backend.hf_deploy --owner-env backend/.env.huggingface
   ```

   This checks the existing private Gradio/free ZeroGPU hardware and gated model
   access, installs only the read token as the Space's `HF_TOKEN` secret, and uploads
   exactly `app.py`, `README.md` and `requirements.txt`. No hardware upgrade, account
   purchase, Space creation or visibility change is performed.
6. Wait for the Space to build/download weights and show **Running**. Inspect model
   access/dependency/runtime errors before continuing. Keep credentials and visitor
   prompts out of copied build/runtime logs.
7. Merge only `TRACE_HF_SPACE_ID` and `TRACE_HF_API_TOKEN` into the VM's existing
   private backend environment, retaining its Cloudflare/Turnstile/other settings.
   Update the protected local recovery copy too. Rebuild the tested backend commit
   and restart its container without deleting volumes. Never copy the write token.
8. `/api/v1/health` and `/api/v1/capabilities` expose `image_fallback_configured`.
   This is a configuration flag, **not** proof of access, GPU capacity or successful
   generation. The frontend Settings disclosure identifies both external services.
9. Run one controlled real fallback, verify image/profile/stages/artifact ownership,
   and record timing and output quality. Test failed capacity and interrupted runs
   with mocks rather than deliberately spending the remaining daily GPU quota.

## Reproducible worker and limits

The worker uses official `black-forest-labs/FLUX.1-schnell` weights at immutable
revision `741f7c3ce8b383c54771c7003378a50191e9efe9`, BF16, four steps, 1024×1024,
guidance zero and maximum sequence length 256. It loads onto CUDA at module
startup as required by ZeroGPU and requests the default 48 GB GPU for up to 45
seconds per execution. Model tokenization limits still apply; images are generated
interpretations, not factual evidence. Real model/GPU latency has not yet been
accepted. Dependencies are pinned in the worker's generated `requirements.txt`.
They are isolated from the existing CPU-only API dependencies/frontend bundle.

To intentionally regenerate the Linux/Python 3.12 worker lock:

```sh
uv pip compile huggingface/image-fallback/requirements.in \
  --python-version 3.12 --python-platform x86_64-manylinux_2_28 \
  --output-file huggingface/image-fallback/requirements.txt
```

Free authenticated accounts currently receive five GPU minutes. Backend calls use
the owner's personal shared quota, not a fresh allowance for each TRACE visitor.
HF resets 24 hours after first GPU usage; Cloudflare's UTC reset is different.
Do not promise an image count until actual GPU usage is measured. Free hardware
and the existing free account remain the financial boundary; no paid overflow
or PRO plan is selected.

Sources: [ZeroGPU hardware/setup/quotas](https://huggingface.co/docs/hub/spaces-zerogpu),
[private REST APIs and token attribution](https://huggingface.co/docs/hub/spaces-api-endpoints),
[Space secrets and management](https://huggingface.co/docs/huggingface_hub/guides/manage-spaces),
[official FLUX model](https://huggingface.co/black-forest-labs/FLUX.1-schnell).

## Verification status

The backend has 245 passing mocked/native tests including 28 new HF routing,
transport, no-duplicate, bounded-response, profile and credential checks. The
frontend typecheck and production build pass. The actual local Gradio 6.30 REST/queue
contract passes with a synthetic PNG, recorded in `evaluation/hf-transport-2026-10-09.json`. These are not a live ZeroGPU generation claim.
Live Space publication and generation require the owner's saved credentials and
model access; production must remain unchanged until those gates are completed.
