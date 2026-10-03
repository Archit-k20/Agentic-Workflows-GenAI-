"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

from openai import OpenAI


def summary(input, api_key=None):
    if api_key:
        # Use OpenAI for potentially better summaries
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize this text:\n{input}"}],
            max_tokens=300,
        )
        return response.choices[0].message.content
    else:
        # Fallback to HuggingFace
        output = get_text_summary_pipeline()(input, min_length=100, max_length=300)
        return output[0]["summary_text"]


from .local_model import get_pipeline as get_text_summary_pipeline
