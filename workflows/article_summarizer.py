"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

from .network import SafeArticle as Article


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
        summary = get_article_summary_pipeline()(
            text, min_length=100, max_length=300, do_sample=False
        )[0]["summary_text"]
        return summary
    except Exception as e:
        return f"Error summarizing article: {e}"


from .local_model import get_pipeline as get_article_summary_pipeline
