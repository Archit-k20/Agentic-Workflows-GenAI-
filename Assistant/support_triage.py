"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.support_triage import (
    _strip_code_fences,
    _load_json,
    _chat_json,
    _normalize_url,
    validate_urls,
    fetch_support_source,
    classify_intent,
    summarize_support_source,
    draft_support_resolution,
    finalize_triage,
    run_support_triage,
    MODEL_NAME,
    MAX_URLS,
    MAX_SOURCE_CHARS,
)


def show_support_triage(api_key=None):
    st.subheader("Support/Triage Agent")
    st.caption(
        "Question -> intent detection -> source retrieval -> grounded answer or escalation"
    )

    if not api_key:
        st.error("OpenAI API key is required for the Support/Triage Agent.")
        return

    question = st.text_area(
        "Support question",
        placeholder="Example: Why is document processing failing after I upload a DOCX file?",
        height=120,
        key="support_triage_question",
    )

    st.markdown("### Support URLs")
    urls = []
    for index in range(5):
        urls.append(
            st.text_input(f"Support URL {index + 1}", key=f"support_triage_url_{index}")
        )

    if "support_triage_result" not in st.session_state:
        st.session_state.support_triage_result = None

    if st.button("Run Support/Triage Agent", type="primary"):
        with st.spinner("Analyzing request and retrieving support context..."):
            try:
                result = run_support_triage(question.strip(), urls, api_key)
            except Exception as exc:
                st.error(f"Support/Triage Agent failed: {exc}")
                return
        st.session_state.support_triage_result = result

    result = st.session_state.support_triage_result
    if not result:
        return

    st.markdown("### Intent Classification")
    st.json(result["intent"])

    if result["invalid_urls"]:
        st.markdown("### Ignored URLs")
        for item in result["invalid_urls"]:
            st.warning(f"Invalid URL skipped: {item}")

    st.markdown("### Retrieved Support Sources")
    for source in result["sources"]:
        with st.expander(f"{source['label']} - {source['title']}"):
            st.markdown(f"**URL:** {source['url']}")
            st.markdown(f"**Summary:** {source['summary']}")
            st.markdown(f"**Relevance:** {source.get('relevance', 'N/A')}")

    if result["source_errors"]:
        st.markdown("### Source Errors")
        for item in result["source_errors"]:
            st.warning(f"{item['label']} ({item['url']}): {item['error']}")

    final = result["final"]
    st.markdown("### Triage Result")
    st.write(f"Resolution type: {final['resolution_type']}")
    st.write(f"Confidence: {final['confidence']:.2f}")
    st.markdown(final["answer"])

    if final["resolution_type"] == "escalate":
        st.error(final["escalation_reason"])

    st.markdown("### Recommended Next Step")
    st.write(final["recommended_next_step"])

    st.markdown("### Citation Check")
    st.json(final["citation_check"])
