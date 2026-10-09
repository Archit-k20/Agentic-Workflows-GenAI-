"""Bounded, authenticated Gradio REST transport. No SDK or GPU in the API image.

Exactly one submission, then one SSE result stream. Never replay a timeout.
The worker returns inline PNG data, avoiding arbitrary artifact URL fetching.
"""

import base64
import io
import json
import os
import re
import time
from urllib.parse import urlsplit

import httpx
from PIL import Image

from . import free_config as cfg
from .policy import Capacity

MAX_RESPONSE = 8 * 1024 * 1024
MAX_IMAGE = 5 * 1024 * 1024
MAX_WAIT = 180


def _status(response):
    if response.is_success:
        return
    if response.status_code in {401, 403, 404}:
        raise Capacity("The private image fallback is not accessible. The operator must check Space access and its read-only token.")
    if response.status_code == 429:
        raise Capacity("Hugging Face GPU capacity or quota is exhausted. Its reset differs from Cloudflare; try again later.")
    raise Capacity("The image fallback is unavailable. Your prompt is retained; retry explicitly.")


def _host(info):
    host = info.get("host", "")
    parts = urlsplit(host)
    if (
        parts.scheme != "https"
        or not re.fullmatch(r"[a-z0-9-]+\.hf\.space", parts.hostname or "")
        or parts.username or parts.password or parts.port
        or parts.path not in {"", "/"} or parts.query or parts.fragment
    ):
        raise Capacity("The image worker did not provide a valid Hugging Face HTTPS endpoint.")
    if info.get("private") is not True:
        raise Capacity("The configured image worker must remain private.")
    if info.get("runtime", {}).get("stage") not in {"RUNNING", "RUNNING_BUILDING", "SLEEPING"}:
        raise Capacity("The image worker is starting, sleeping or unavailable. Retry explicitly after it is running.")
    return host.rstrip("/")


def _lines(stream, bounded):
    buffer, size = b"", 0
    for chunk in stream.iter_bytes():
        bounded()
        size += len(chunk)
        if size > MAX_RESPONSE:
            raise ValueError("The image worker response exceeded the permitted size.")
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            yield line.rstrip(b"\r").decode("utf-8")
    if buffer:
        yield buffer.decode("utf-8")


def _payload(data):
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        raise ValueError("The image worker returned an invalid result.")
    result = data[0]
    if result.get("model") != cfg.HF_IMAGE_MODEL or result.get("revision") != cfg.HF_IMAGE_REVISION or result.get("steps") != 4:
        raise ValueError("The image worker's model profile changed. The operator must review it before use.")
    try:
        raw = base64.b64decode(result["image"], validate=True)
        if len(raw) > MAX_IMAGE:
            raise ValueError()
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != "PNG" or image.size != (1024, 1024):
                raise ValueError()
            image.verify()
    except (KeyError, TypeError, ValueError, OSError):
        raise ValueError("The image worker returned an unreadable or oversized PNG.") from None
    return result


def generate(prompt, deadline, check):
    if not cfg.image_fallback_configured():
        raise Capacity("The private image fallback is not configured.")
    stop = min(deadline, time.monotonic() + MAX_WAIT)

    def bounded(network_limit=15):
        check()
        remaining = stop - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Image fallback wait limit reached. Generation may have started; no request was replayed. Retry explicitly.")
        return min(network_limit, remaining)

    token = os.environ["TRACE_HF_API_TOKEN"]
    space = os.environ["TRACE_HF_SPACE_ID"]
    headers = {"Authorization": "Bearer " + token}
    try:
        with httpx.Client(headers=headers, follow_redirects=False, timeout=15) as client:
            response = client.get("https://huggingface.co/api/spaces/" + space, timeout=bounded())
            _status(response)
            info = response.json()
            if info.get("id") != space:
                raise ValueError("The configured image Space did not match the returned identity.")
            host = _host(info)
            # Safe readiness GET can wake a sleeping Space before any generation.
            response = client.get(host + "/config", timeout=bounded())
            _status(response)
            endpoint = host + "/gradio_api/call/generate"
            response = client.post(endpoint, json={"data": [prompt]}, timeout=bounded())
            _status(response)
            event_id = response.json().get("event_id", "")
            if not isinstance(event_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", event_id):
                raise ValueError("The image worker returned an invalid request identifier.")
            event, data = "", []
            # Gradio's queue can heartbeat every 15 seconds. Leave headroom for
            # that heartbeat while retaining the overall bounded wait.
            with client.stream("GET", endpoint + "/" + event_id, timeout=bounded(30)) as stream:
                _status(stream)
                for line in _lines(stream, bounded):
                    if line.startswith("event:"):
                        event = line[6:].strip()
                    elif line.startswith("data:"):
                        data.append(line[5:].lstrip())
                    elif not line:
                        if event == "error":
                            # Never expose remote exceptions, prompts, paths or credentials.
                            raise Capacity("Hugging Face could not complete generation: GPU quota, capacity or worker failure. Your prompt is retained; retry explicitly.")
                        if event == "complete":
                            return _payload(json.loads("\n".join(data)))
                        event, data = "", []
            raise Capacity("The image fallback stream ended without a result. Generation may have started; retry explicitly.")
    except httpx.RequestError:
        raise Capacity("The image fallback connection was interrupted. Generation may have started; no request was replayed. Retry explicitly.") from None
    except (json.JSONDecodeError, UnicodeError):
        raise ValueError("The image worker returned an invalid response.") from None
