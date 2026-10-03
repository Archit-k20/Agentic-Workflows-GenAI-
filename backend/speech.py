"""CPU Kokoro pipelines and real, downloadable MP3 artifacts."""

from functools import lru_cache
import subprocess
import tempfile
from pathlib import Path

REVISION = "f3ff3571791e39611d31c381e3a41a3af07b4987"


@lru_cache(maxsize=1)
def assets():
    from huggingface_hub import snapshot_download
    from kokoro import KModel

    folder = Path(
        snapshot_download(
            "hexgrad/Kokoro-82M",
            revision=REVISION,
            allow_patterns=[
                "config.json",
                "kokoro-v1_0.pth",
                *[
                    "voices/" + voice + ".pt"
                    for voice in (
                        "af_heart",
                        "af_bella",
                        "af_nicole",
                        "am_michael",
                        "am_fenrir",
                        "bf_emma",
                    )
                ],
            ],
        )
    )
    model = (
        KModel(
            repo_id="hexgrad/Kokoro-82M",
            config=str(folder / "config.json"),
            model=str(folder / "kokoro-v1_0.pth"),
        )
        .to("cpu")
        .eval()
    )
    return model, folder


@lru_cache(maxsize=2)
def pipeline(accent):
    from kokoro import KPipeline

    model, folder = assets()
    return (
        KPipeline(lang_code=accent, model=model, repo_id="hexgrad/Kokoro-82M"),
        folder,
    )


def synthesize(text, voice, path, check=lambda: None):
    import numpy as np
    import soundfile as sf

    engine, folder = pipeline("b" if voice.startswith("b") else "a")
    audio = []
    # KPipeline applies sentence splitting; each returned segment is real speech.
    for _, _, samples in engine(
        text, voice=str(folder / "voices" / (voice + ".pt")), split_pattern=r"\n+"
    ):
        check()
        audio.append(samples.numpy() if hasattr(samples, "numpy") else samples)
    if not audio:
        raise ValueError("Speech engine returned no audio.")
    with tempfile.TemporaryDirectory(prefix="trace-audio-") as tmp:
        wav = Path(tmp) / "voice.wav"
        sf.write(wav, np.concatenate(audio), 24000)
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(wav),
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "128k",
                "-f",
                "mp3",
                str(path),
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
