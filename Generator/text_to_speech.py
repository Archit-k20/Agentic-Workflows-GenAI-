from openai import OpenAI
from dotenv import load_dotenv
import os

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_speech(text, voice="alloy", api_key=None):
    try:
        client = OpenAI(api_key=api_key)
        # ... rest of the function
        response = client.audio.speech.create(
            model="tts-1",  
            voice=voice,
            input=text
        )
        out_path = "tts_output.mp3"
        with open(out_path, "wb") as f:
            f.write(response.content)
        return out_path
    except Exception as e:
        return f"Error: {e}"
