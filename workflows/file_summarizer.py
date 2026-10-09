"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

import fitz

import docx

from io import BytesIO


def extract_text_from_pdf(file_obj):
    text = ""
    try:
        file_obj.seek(0)
        pdf_bytes = file_obj.read()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"


def extract_text_from_docx(file_obj):
    try:
        file_obj.seek(0)
        doc = docx.Document(BytesIO(file_obj.read()))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {e}"


def summarize_file(file, api_key=None):
    file_name = file.name.lower()
    if file_name.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    elif file_name.endswith(".docx"):
        text = extract_text_from_docx(file)
    else:
        return "Unsupported file type. Please upload a PDF or DOCX file."

    if not text.strip():
        return "The file appears to be empty."

    try:
        if len(text) > 4000:
            text = text[:4000]
        summary = get_file_summary_pipeline()(
            text, min_length=100, max_length=300, do_sample=False
        )[0]["summary_text"]
        return summary
    except Exception as e:
        return f"Error during summarization: {e}"


from .local_model import get_pipeline as get_file_summary_pipeline
