"""Public, fixed free-mode profiles. Secrets are read only by provider adapters."""

import os
from threading import RLock

CHAT_MODEL = "@cf/qwen/qwen3-30b-a3b-fp8"
CODE_MODEL = "@cf/qwen/qwen2.5-coder-32b-instruct"
IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
LOCAL_DIGEST = "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"
LOCAL_MODEL = "qwen3.5:4b"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
MAX_TOKENS = 12000
CPU_GATE = RLock()
VOICES = [
    {"id": "af_heart", "name": "Heart", "accent": "American English"},
    {"id": "af_bella", "name": "Bella", "accent": "American English"},
    {"id": "af_nicole", "name": "Nicole", "accent": "American English"},
    {"id": "am_michael", "name": "Michael", "accent": "American English"},
    {"id": "am_fenrir", "name": "Fenrir", "accent": "American English"},
    {"id": "bf_emma", "name": "Emma", "accent": "British English"},
]
OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def configured():
    return bool(
        os.environ.get("TRACE_CLOUDFLARE_ACCOUNT_ID")
        and os.environ.get("TRACE_CLOUDFLARE_API_TOKEN")
    )
