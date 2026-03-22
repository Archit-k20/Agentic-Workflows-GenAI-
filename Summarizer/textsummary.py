from openai import OpenAI
import torch
from transformers import pipeline

text_summary = None


def get_text_summary_pipeline():
    global text_summary
    if text_summary is None:
        kwargs = {"model": "sshleifer/distilbart-cnn-12-6"}
        if torch.cuda.is_available():
            kwargs["torch_dtype"] = torch.bfloat16
        text_summary = pipeline("summarization", **kwargs)
    return text_summary

def summary(input, api_key=None):
    if api_key:
        # Use OpenAI for potentially better summaries
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize this text:\n{input}"}],
            max_tokens=300
        )
        return response.choices[0].message.content
    else:
        # Fallback to HuggingFace
        output = get_text_summary_pipeline()(input, min_length=100, max_length=300)
        return output[0]['summary_text']
