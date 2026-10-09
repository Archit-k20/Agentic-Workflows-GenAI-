---
title: TRACE Image Fallback
emoji: 🖼️
colorFrom: gray
colorTo: red
sdk: gradio
sdk_version: 6.30.0
python_version: 3.12
app_file: app.py
pinned: false
license: apache-2.0
---

Private image-only ZeroGPU service for TRACE. This does not host the TRACE website.

Model: `black-forest-labs/FLUX.1-schnell`, immutable revision
`741f7c3ce8b383c54771c7003378a50191e9efe9`. Four inference steps, 1024×1024 PNG,
guidance 0 and maximum sequence length 256. One GPU request at a time.

Required secret: `HF_TOKEN`, read-only access to the gated official model.
The owner must review its model-access conditions themselves. Keep this Space private.
No token, prompt log, application session, uploaded document or API credential belongs in this repository.

API: `/generate`, one string prompt (nonempty, at most 2,048 characters), one JSON
output with inline PNG base64, pinned model/revision, seed, steps, dimensions and
measured inference duration. TRACE validates the profile and returns its own
session-owned image artifact. Raw provider errors are not returned to visitors.

The module places weights on CUDA at startup as required by ZeroGPU. The GPU
function requests at most 45 seconds on the default 48 GB GPU; measure latency
before reducing that duration. Gradio queue length is bounded at four. A queue
or GPU quota failure never substitutes a sample image.

Keep free hardware. Hosting this Space does not provide unlimited generation;
authenticated API calls consume the calling owner's shared personal GPU quota.
