from newspaper import Article
from transformers import pipeline
import torch

article_summary = None


def get_article_summary_pipeline():
    global article_summary
    if article_summary is None:
        kwargs = {"model": "sshleifer/distilbart-cnn-12-6"}
        if torch.cuda.is_available():
            kwargs["torch_dtype"] = torch.bfloat16
        article_summary = pipeline("summarization", **kwargs)
    return article_summary

def summarize_article(url, api_key=None):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        if not text.strip():
            return "Could not extract text from the URL."

        if len(text) > 4000:
            text = text[:4000]
        summary = get_article_summary_pipeline()(text, min_length=100, max_length=300, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        return f"Error summarizing article: {e}"
