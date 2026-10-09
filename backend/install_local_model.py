"""Install the tested Ollama manifest and checksum-addressed blobs.

The public model tag is mutable. This setup command never changes the accepted
digest, and publishes the manifest only after all original blobs are verified.
Run as a one-off setup service with the Ollama volume mounted at /ollama.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.request import urlopen

from .free_config import LOCAL_DIGEST

PIN = Path(__file__).with_name("assets") / "qwen3.5-4b.manifest.json"
REGISTRY = "https://registry.ollama.ai/v2/library/qwen3.5/blobs/"
CHUNK = 1024 * 1024


def verified(path, expected, size):
    if not path.is_file() or path.stat().st_size != size:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest() == expected


def install(models_dir, manifest_path=PIN, opener=urlopen):
    raw = Path(manifest_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != LOCAL_DIGEST:
        raise ValueError("The bundled model manifest differs from the tested pin; setup stopped.")
    manifest = json.loads(raw)
    entries = [manifest["config"], *manifest["layers"]]
    # Validate every descriptor before writing or downloading anything.
    for entry in entries:
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", entry["digest"]):
            raise ValueError("Invalid pinned blob digest.")
        if not isinstance(entry["size"], int) or not 0 < entry["size"] <= 4 * 1024**3:
            raise ValueError("Invalid pinned blob size.")
    models_dir = Path(models_dir)
    blobs = models_dir / "blobs"
    blobs.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for entry in entries:
        digest, size = entry["digest"][7:], entry["size"]
        destination = blobs / ("sha256-" + digest)
        if verified(destination, digest, size):
            continue
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=blobs, prefix=".trace-download-", delete=False) as output:
                temporary = Path(output.name)
                hashed, received = hashlib.sha256(), 0
                with opener(REGISTRY + entry["digest"], timeout=30) as response:
                    if not response.geturl().startswith("https://"):
                        raise ValueError("Pinned model download must use HTTPS.")
                    for chunk in iter(lambda: response.read(CHUNK), b""):
                        received += len(chunk)
                        if received > size:
                            raise ValueError("Pinned model blob exceeds its declared size.")
                        hashed.update(chunk)
                        output.write(chunk)
                if received != size or hashed.hexdigest() != digest:
                    raise ValueError("Pinned model blob checksum/size mismatch; setup stopped.")
                output.flush()
                os.fsync(output.fileno())
            temporary.replace(destination)
            downloaded += 1
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    target = models_dir / "manifests/registry.ollama.ai/library/qwen3.5/4b"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".trace-manifest-", delete=False) as output:
            temporary = Path(output.name)
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"model": "qwen3.5:4b", "digest": LOCAL_DIGEST, "verified_blobs": len(entries), "downloaded_blobs": downloaded}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-dir", type=Path, default=Path("/ollama/models"))
    args = parser.parse_args()
    print(json.dumps(install(args.models_dir), indent=2))


if __name__ == "__main__":
    main()
