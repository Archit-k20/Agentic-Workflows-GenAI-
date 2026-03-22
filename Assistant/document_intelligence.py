import json
import os
import re
from io import BytesIO

import docx
import fitz
import pytesseract
import streamlit as st
from PIL import Image
from openai import OpenAI


MODEL_NAME = "gpt-4o-mini"
MAX_TEXT_CHARS = 14000
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?)\b",
    re.IGNORECASE,
)
TASK_PATTERN = re.compile(
    r"\b(?:action item|todo|to-do|follow up|follow-up|deadline|deliver|submit|review|approve|call|email|meet)\b",
    re.IGNORECASE,
)


if os.path.exists(DEFAULT_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH


def _strip_code_fences(value):
    cleaned = value.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _load_json(value, fallback):
    try:
        return json.loads(_strip_code_fences(value))
    except json.JSONDecodeError:
        return fallback


def _chat_json(client, system_prompt, user_prompt, fallback):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or ""
    return _load_json(content, fallback)


def extract_text_from_pdf(uploaded_file):
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    text_chunks = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page in document:
            text_chunks.append(page.get_text())

    return "\n".join(text_chunks).strip()


def extract_text_from_docx(uploaded_file):
    uploaded_file.seek(0)
    document = docx.Document(BytesIO(uploaded_file.read()))
    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_txt(uploaded_file):
    uploaded_file.seek(0)
    content = uploaded_file.read()
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="ignore").strip()
    return str(content).strip()


def extract_text_from_image(uploaded_file):
    uploaded_file.seek(0)
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image).strip()


def extract_document_text(uploaded_file):
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
        source_type = "pdf"
    elif file_name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
        source_type = "docx"
    elif file_name.endswith(".txt"):
        text = extract_text_from_txt(uploaded_file)
        source_type = "txt"
    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image(uploaded_file)
        source_type = "image"
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, TXT, PNG, JPG, or JPEG.")

    return {
        "name": uploaded_file.name,
        "source_type": source_type,
        "text": text[:MAX_TEXT_CHARS],
    }


def fallback_document_analysis(document):
    text = document["text"]
    sentences = [line.strip() for line in re.split(r"[\n\.]+", text) if line.strip()]
    action_items = []

    for sentence in sentences:
        if TASK_PATTERN.search(sentence):
            due_dates = DATE_PATTERN.findall(sentence)
            action_items.append(
                {
                    "task": sentence[:220],
                    "owner": "Unknown",
                    "due_date": due_dates[0] if due_dates else "Not specified",
                    "priority": "Medium",
                }
            )

    people = sorted(set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)))[:10]
    emails = sorted(set(re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)))[:10]
    dates = DATE_PATTERN.findall(text)[:10]

    if not action_items and sentences:
        action_items.append(
            {
                "task": sentences[0][:220],
                "owner": "Unknown",
                "due_date": dates[0] if dates else "Not specified",
                "priority": "Medium",
            }
        )

    return {
        "document_type": document["source_type"].upper(),
        "summary": text[:600] if text else "No text extracted from the document.",
        "entities": {
            "people": people,
            "organizations": [],
            "emails": emails,
            "dates": dates,
        },
        "action_items": action_items[:8],
        "risks": ["Extraction used fallback heuristics; verify important details manually."],
    }


def analyze_document(document, client):
    fallback = fallback_document_analysis(document)
    return _chat_json(
        client,
        (
            "You analyze business and operational documents. "
            "Return JSON with document_type, summary, entities, action_items, and risks. "
            "Entities must include people, organizations, emails, and dates. "
            "Each action item must include task, owner, due_date, and priority. "
            "If something is unknown, say 'Unknown' or 'Not specified'."
        ),
        (
            f"Document name: {document['name']}\n"
            f"Source type: {document['source_type']}\n"
            f"Document text:\n{document['text']}"
        ),
        fallback,
    )


def run_document_intelligence(uploaded_files, api_key):
    if not uploaded_files:
        raise ValueError("Please upload at least one file for Document Intelligence.")

    client = OpenAI(api_key=api_key)
    documents = []
    errors = []

    for uploaded_file in uploaded_files[:3]:
        try:
            document = extract_document_text(uploaded_file)
            if not document["text"].strip():
                raise ValueError("No text could be extracted from the file.")
            analysis = analyze_document(document, client)
            documents.append(
                {
                    "name": document["name"],
                    "source_type": document["source_type"],
                    "text_preview": document["text"][:800],
                    "analysis": analysis,
                }
            )
        except Exception as exc:
            errors.append({"name": uploaded_file.name, "error": str(exc)})

    if not documents:
        raise ValueError("Document Intelligence could not process any uploaded files.")

    return {"documents": documents, "errors": errors}


def show_document_intelligence(api_key=None):
    st.subheader("Document Intelligence")
    st.caption("Ingest -> extract text/OCR -> classify -> extract entities -> action items")

    if not api_key:
        st.error("OpenAI API key is required for Document Intelligence.")
        return

    uploaded_files = st.file_uploader(
        "Upload up to 3 files",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="document_intelligence_uploader",
    )

    if "document_intelligence_result" not in st.session_state:
        st.session_state.document_intelligence_result = None

    if st.button("Run Document Intelligence", type="primary"):
        with st.spinner("Extracting text and analyzing documents..."):
            try:
                result = run_document_intelligence(uploaded_files, api_key)
            except Exception as exc:
                st.error(f"Document Intelligence failed: {exc}")
                return
        st.session_state.document_intelligence_result = result

    result = st.session_state.document_intelligence_result
    if not result:
        return

    for item in result["documents"]:
        analysis = item["analysis"]
        with st.expander(f"{item['name']} ({item['source_type'].upper()})", expanded=True):
            st.markdown("### Summary")
            st.write(analysis.get("summary", "No summary available."))

            st.markdown("### Classification")
            st.write(analysis.get("document_type", "Unknown"))

            st.markdown("### Entities")
            st.json(analysis.get("entities", {}))

            st.markdown("### Action Items")
            action_items = analysis.get("action_items", [])
            if action_items:
                st.json(action_items)
            else:
                st.write("No action items detected.")

            st.markdown("### Risks / Notes")
            risks = analysis.get("risks", [])
            if risks:
                for risk in risks:
                    st.write(f"- {risk}")
            else:
                st.write("No major risks flagged.")

    if result["errors"]:
        st.markdown("### Processing Errors")
        for item in result["errors"]:
            st.warning(f"{item['name']}: {item['error']}")
