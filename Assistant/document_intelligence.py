"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.document_intelligence import (
    _strip_code_fences,
    _load_json,
    _chat_json,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_text_from_image,
    extract_document_text,
    fallback_document_analysis,
    analyze_document,
    run_document_intelligence,
    MODEL_NAME,
    MAX_TEXT_CHARS,
    DEFAULT_TESSERACT_PATH,
    DATE_PATTERN,
    TASK_PATTERN,
)


def show_document_intelligence(api_key=None):
    st.subheader("Document Intelligence")
    st.caption(
        "Ingest -> extract text/OCR -> classify -> extract entities -> action items"
    )

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
        with st.expander(
            f"{item['name']} ({item['source_type'].upper()})", expanded=True
        ):
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
