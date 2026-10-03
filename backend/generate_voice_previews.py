"""Regenerate the six bundled preview assets with the pinned Kokoro profile."""

import argparse
from pathlib import Path
from .free_config import VOICES, CPU_GATE
from .speech import synthesize

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True)
args = parser.parse_args()
folder = Path(args.output)
folder.mkdir(parents=True, exist_ok=True)
with CPU_GATE:
    for voice in VOICES:
        synthesize(
            "Welcome to Trace. Turn your ideas into clear, useful results.",
            voice["id"],
            folder / (voice["id"] + ".mp3"),
        )
        print("Generated " + voice["id"], flush=True)
