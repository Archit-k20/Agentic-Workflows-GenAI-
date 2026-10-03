"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

from openai import OpenAI

import os
import tempfile


def generate_speech(text, voice="alloy", api_key=None, output_path=None):
    try:
        client = OpenAI(api_key=api_key)
        # ... rest of the function
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        if output_path is None:
            fd, out_path = tempfile.mkstemp(suffix=".mp3", prefix="trace-speech-")
            os.close(fd)
        else:
            out_path = str(output_path)
        with open(out_path, "wb") as f:
            f.write(response.content)
        return out_path
    except Exception as e:
        return f"Error: {e}"
