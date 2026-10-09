"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.research_agent import (
    _strip_code_fences,
    _load_json,
    _chat_json,
    _chat_text,
    validate_urls,
    validate_citations,
    plan_research,
    _normalize_url,
    fetch_source,
    summarize_source,
    synthesize_report,
    critique_report,
    revise_report,
    run_research_agent,
    MODEL_NAME,
    MAX_URLS,
    MAX_SOURCE_CHARS,
    CITATION_PATTERN,
)


def show_research_agent(api_key=None):
    st.subheader("Research Agent")
    st.caption("Planner -> source reader -> source summarizer -> synthesis -> critique")

    if not api_key:
        st.error("OpenAI API key is required for the Research Agent.")
        return

    topic = st.text_area(
        "Research topic",
        placeholder="Example: Evaluate the recent progress and risks of small language models for enterprise support bots.",
        height=100,
    )

    st.markdown("### Source URLs")
    urls = []
    for index in range(5):
        urls.append(
            st.text_input(f"URL {index + 1}", key=f"research_agent_url_{index}")
        )

    if "research_agent_result" not in st.session_state:
        st.session_state.research_agent_result = None

    if st.button("Run Research Agent", type="primary"):
        if not topic.strip():
            st.warning("Please enter a research topic before running the agent.")
            return

        with st.spinner("Planning, reading sources, and drafting the report..."):
            try:
                result = run_research_agent(topic.strip(), urls, api_key)
            except Exception as exc:
                st.error(f"Research Agent failed: {exc}")
                return
        st.session_state.research_agent_result = result

    result = st.session_state.research_agent_result
    if not result:
        return

    st.markdown("### Research Plan")
    st.json(result["plan"])

    if result["invalid_urls"]:
        st.markdown("### Ignored URLs")
        for item in result["invalid_urls"]:
            st.warning(f"Invalid URL skipped: {item}")

    st.markdown("### Source Digests")
    for source in result["sources"]:
        with st.expander(f"{source['label']} - {source['title']}"):
            st.markdown(f"**URL:** {source['url']}")
            st.markdown(f"**Summary:** {source['summary']}")
            points = source.get("key_points", [])
            if points:
                st.markdown("**Key Points**")
                for point in points:
                    st.write(f"- {point}")
            st.markdown(f"**Relevance:** {source.get('relevance', 'N/A')}")

    if result["source_errors"]:
        st.markdown("### Source Errors")
        for item in result["source_errors"]:
            st.warning(f"{item['label']} ({item['url']}): {item['error']}")

    st.markdown("### Critique")
    critique = result["critique"]
    st.write(f"Passes review: {'Yes' if critique.get('passes_review') else 'No'}")
    issues = critique.get("issues", [])
    if issues:
        for issue in issues:
            st.write(f"- {issue}")
    else:
        st.write("No major grounding issues were flagged.")

    st.markdown("### Citation Check")
    citation_check = result["citation_check"]
    st.write(f"Has citations: {'Yes' if citation_check['has_any_citation'] else 'No'}")
    st.write(
        f"Cited labels: {', '.join(citation_check['cited_labels']) if citation_check['cited_labels'] else 'None'}"
    )
    if citation_check["unknown_labels"]:
        st.error(
            f"Unknown citation labels found: {', '.join(citation_check['unknown_labels'])}"
        )

    st.markdown("### Final Report")
    # Ensure final_report is displayed as markdown string
    report_content = result["final_report"]
    if isinstance(report_content, dict):
        report_content = str(report_content)
    st.markdown(report_content)


def main():
    st.set_page_config(page_title="GenAI Research Agent", layout="wide")

    # Sidebar for API Key
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            st.success("API Key provided")
        else:
            st.info("Enter your API Key to begin")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("Maintained by **Archit Kumar**")
        st.markdown(
            "[LinkedIn](https://www.linkedin.com/in/archit-kumar-aa6375259) | [GitHub](https://github.com/)"
        )

    show_research_agent(api_key)


if __name__ == "__main__":
    main()
