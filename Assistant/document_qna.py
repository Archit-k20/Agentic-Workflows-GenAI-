"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.document_qna import (
    split_text,
    extract_pdf_text,
    extract_docx_text,
    uploaded_file_to_documents,
    build_document_vectorstore,
    answer_with_context,
    MAX_FILES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def show_document_qna(uploaded_files, api_key=None):
    st.title("Document QnA Tool")

    if not api_key:
        st.error("OpenAI API key is required")
        return

    if not uploaded_files:
        st.info("Please upload at least one document to begin.")
        return

    if "document_qna_vectorstore" not in st.session_state:
        st.session_state.document_qna_vectorstore = None
    if "document_qna_errors" not in st.session_state:
        st.session_state.document_qna_errors = []

    if st.button("Process Files"):
        with st.spinner("Processing documents..."):
            try:
                vectorstore, errors = build_document_vectorstore(
                    uploaded_files, api_key
                )
                st.session_state.document_qna_vectorstore = vectorstore
                st.session_state.document_qna_errors = errors
                st.success("Documents processed and ready for querying.")
            except Exception as exc:
                st.session_state.document_qna_vectorstore = None
                st.error(f"Error processing files: {exc}")
                return

    for error in st.session_state.document_qna_errors:
        st.warning(error)

    query = st.text_input("Ask a question about your documents:")
    if query:
        vectorstore = st.session_state.document_qna_vectorstore
        if vectorstore is None:
            st.warning("Please process documents first.")
            return

        with st.spinner("Searching for answers..."):
            try:
                retrieved_docs = vectorstore.similarity_search(query, k=4)
                answer = answer_with_context(query, retrieved_docs, api_key)
                st.markdown("### Answer")
                st.write(answer)
                st.markdown("### Retrieved Sources")
                for index, doc in enumerate(retrieved_docs, start=1):
                    source = doc.metadata.get("source", "Uploaded document")
                    chunk = doc.metadata.get("chunk", index)
                    st.code(f"[S{index}] {source}, chunk {chunk}")
            except Exception as exc:
                st.error(f"Error answering question: {exc}")
