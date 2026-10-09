"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

from urllib.parse import urlparse

from .network import fetch_html

from bs4 import BeautifulSoup

from .network import SafeArticle as Article

from .runtime import client as OpenAI

MAX_URLS = 3

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 160


def is_valid_url(url):
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    cleaned = " ".join(text.split())
    while start < len(cleaned):
        end = start + chunk_size
        chunks.append(cleaned[start:end])
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)
    return [chunk for chunk in chunks if chunk.strip()]


def fetch_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text and article.text.strip():
            return article.title or url, article.text.strip()
    except Exception:
        pass

    soup = BeautifulSoup(fetch_html(url), "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = " ".join(soup.get_text(" ").split())
    if not text:
        raise ValueError("Could not extract readable text from the URL.")
    return title, text


def urls_to_documents(urls):
    from langchain_core.documents import Document

    documents = []
    errors = []

    for url in urls[:MAX_URLS]:
        try:
            title, text = fetch_article_text(url)
            for index, chunk in enumerate(split_text(text), start=1):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": url, "title": title, "chunk": index},
                    )
                )
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    if not documents:
        raise ValueError(
            "No URLs could be processed. Please check the links and try again."
        )

    return documents, errors


def build_url_vectorstore(urls, api_key):
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings

    documents, errors = urls_to_documents(urls)
    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore, errors


def answer_with_context(question, docs, api_key):
    context_blocks = []
    for index, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "URL source")
        source = doc.metadata.get("source", "")
        chunk = doc.metadata.get("chunk", index)
        context_blocks.append(
            f"[S{index}] Title: {title}\nURL: {source}\nChunk: {chunk}\n{doc.page_content}"
        )

    context = "\n\n".join(context_blocks)
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the provided URL context. "
                    "If the answer is not present, say the sources do not contain enough information. "
                    "Cite sources inline using labels like [S1]."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nURL context:\n{context}",
            },
        ],
    )
    return response.choices[0].message.content or "No answer generated."
