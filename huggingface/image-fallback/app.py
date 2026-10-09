"""Private image-only worker. No TRACE visitor credentials or uploaded documents."""

import base64
import io
import secrets
import time

import gradio as gr
import spaces
import torch
from diffusers import FluxPipeline

MODEL = "black-forest-labs/FLUX.1-schnell"
REVISION = "741f7c3ce8b383c54771c7003378a50191e9efe9"

# ZeroGPU requires module-level CUDA placement, not lazy loading in GPU calls.
# HF_TOKEN is a read-only Space secret. Revision fixes weights to a reviewed commit.
pipe = FluxPipeline.from_pretrained(
    MODEL, revision=REVISION, torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
).to("cuda")


@spaces.GPU(duration=45)
@torch.inference_mode()
def generate(prompt):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 2048:
        raise gr.Error("Use a non-empty image prompt of at most 2,048 characters.")
    seed = secrets.randbelow(2**31)
    started = time.monotonic()
    image = pipe(
        prompt=prompt, height=1024, width=1024,
        guidance_scale=0.0, num_inference_steps=4,
        max_sequence_length=256,
        generator=torch.Generator("cpu").manual_seed(seed),
    ).images[0]
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return {
        "image": base64.b64encode(buffer.getvalue()).decode("ascii"),
        "model": MODEL, "revision": REVISION, "seed": seed,
        "steps": 4, "width": image.width, "height": image.height,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


with gr.Blocks(title="TRACE private image worker") as demo:
    gr.Markdown("# TRACE image worker\nPrivate backend service. Four-step FLUX.1-schnell; shared ZeroGPU quotas apply.")
    prompt = gr.Textbox(label="Image prompt", max_lines=8)
    result = gr.JSON(label="TRACE transport result")
    run = gr.Button("Generate")
    run.click(generate, inputs=prompt, outputs=result, api_name="generate", concurrency_limit=1)

demo.queue(max_size=4, default_concurrency_limit=1).launch(show_error=False)
