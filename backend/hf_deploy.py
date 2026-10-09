"""Publish the private free image worker using local-only scoped write credentials.

Never sends the deployment token to TRACE's API server or Space secrets.
Does not create Spaces, change visibility, purchase hardware or accept model terms.
"""

import argparse
import json
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

from . import free_config as cfg


def read_env(path):
    values = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")
    return values


def publish(values):
    space = values.get("TRACE_HF_SPACE_ID", "")
    runtime_token = values.get("TRACE_HF_API_TOKEN", "")
    deploy_token = values.get("TRACE_HF_DEPLOY_TOKEN", "")
    if not space or not runtime_token or not deploy_token:
        raise ValueError("Save the Space ID and both scoped tokens in the private owner environment file.")
    read = HfApi(token=runtime_token)
    write = HfApi(token=deploy_token)
    info = read.space_info(space)
    if info.private is not True or info.sdk != "gradio":
        raise ValueError("Use the existing private Gradio Space; visibility will not be changed.")
    hardware = write.get_space_runtime(space)
    selected = hardware.requested_hardware or hardware.hardware
    if selected != "zero-a10g" or hardware.hardware not in {None, "zero-a10g"}:
        raise ValueError("The Space must already use free ZeroGPU hardware; no upgrade will be requested.")
    # A tiny pinned file proves model access without downloading large weights.
    hf_hub_download(cfg.HF_IMAGE_MODEL, "model_index.json", revision=cfg.HF_IMAGE_REVISION, token=runtime_token)
    write.add_space_secret(space, "HF_TOKEN", runtime_token)
    source = Path(__file__).resolve().parents[1] / "huggingface" / "image-fallback"
    commit = write.upload_folder(
        repo_id=space, repo_type="space", folder_path=source,
        allow_patterns=["README.md", "app.py", "requirements.txt"],
        commit_message="Add pinned TRACE private ZeroGPU image worker",
    )
    return {"space": space, "commit": commit.oid, "private": True, "hardware": "zero-a10g", "model": cfg.HF_IMAGE_MODEL, "revision": cfg.HF_IMAGE_REVISION}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner-env", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(publish(read_env(args.owner_env)), indent=2))
    except Exception as exc:
        # SDK exceptions can include authorization headers or remote paths.
        print(json.dumps({"published": False, "error_type": type(exc).__name__, "message": "Worker setup failed. Check scoped tokens, model access and existing private ZeroGPU hardware; no paid upgrade was requested."}))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
