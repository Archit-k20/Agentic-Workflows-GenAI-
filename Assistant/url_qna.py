"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.url_qna import (
    is_valid_url,
    split_text,
    fetch_article_text,
    urls_to_documents,
    build_url_vectorstore,
    answer_with_context,
    MAX_URLS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def show_url_qna(api_key=None):
    if not api_key:
        st.error("OpenAI API key is required")
        return

    st.markdown("Enter up to 3 URLs to begin.")
    urls = []
    for index in range(MAX_URLS):
        urls.append(
            st.text_input(f"URL {index + 1}", key=f"url_qna_url_{index}").strip()
        )

    if "url_qna_vectorstore" not in st.session_state:
        st.session_state.url_qna_vectorstore = None
    if "url_qna_errors" not in st.session_state:
        st.session_state.url_qna_errors = []

    if st.button("Process URLs"):
        valid_urls = [url for url in urls if is_valid_url(url)]
        if not valid_urls:
            st.error(
                "Please enter at least one valid URL starting with http:// or https://"
            )
            return

        with st.spinner("Loading and indexing URL content..."):
            try:
                vectorstore, errors = build_url_vectorstore(valid_urls, api_key)
                st.session_state.url_qna_vectorstore = vectorstore
                st.session_state.url_qna_errors = errors
                st.success("URLs indexed and ready for questions.")
            except Exception as exc:
                st.session_state.url_qna_vectorstore = None
                st.error(f"Error processing URLs: {exc}")
                return

    for error in st.session_state.url_qna_errors:
        st.warning(error)

    query = st.text_input("Ask a question about the URLs:")
    if query:
        vectorstore = st.session_state.url_qna_vectorstore
        if vectorstore is None:
            st.warning("Please process URLs first before asking questions.")
            return

        with st.spinner("Searching for answers..."):
            try:
                retrieved_docs = vectorstore.similarity_search(query, k=4)
                answer = answer_with_context(query, retrieved_docs, api_key)
                st.markdown("### Answer")
                st.write(answer)
                st.markdown("### Retrieved Sources")
                for index, doc in enumerate(retrieved_docs, start=1):
                    source = doc.metadata.get("source", "")
                    title = doc.metadata.get("title", "URL source")
                    st.code(f"[S{index}] {title}\n{source}")
            except Exception as exc:
                st.error(f"Error answering question: {exc}")
