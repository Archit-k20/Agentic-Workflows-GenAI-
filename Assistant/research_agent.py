# import json
# import re
# from urllib.parse import urlparse

# import streamlit as st
# from newspaper import Article
# from openai import OpenAI


# MODEL_NAME = "gpt-4o-mini"
# MAX_URLS = 5
# MAX_SOURCE_CHARS = 12000
# CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


# def _strip_code_fences(value):
#     cleaned = value.strip()
#     if cleaned.startswith("```"):
#         lines = cleaned.splitlines()
#         if lines:
#             lines = lines[1:]
#         if lines and lines[-1].strip() == "```":
#             lines = lines[:-1]
#         cleaned = "\n".join(lines).strip()
#     return cleaned


# def _load_json(value, fallback):
#     try:
#         return json.loads(_strip_code_fences(value))
#     except json.JSONDecodeError:
#         return fallback


# def _chat_json(client, system_prompt, user_prompt, fallback):
#     response = client.chat.completions.create(
#         model=MODEL_NAME,
#         response_format={"type": "json_object"},
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         temperature=0.2,
#     )
#     content = response.choices[0].message.content or ""
#     return _load_json(content, fallback)


# def _chat_text(client, system_prompt, user_prompt):
#     response = client.chat.completions.create(
#         model=MODEL_NAME,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         temperature=0.3,
#     )
#     return (response.choices[0].message.content or "").strip()


# def validate_urls(urls):
#     valid_urls = []
#     invalid_urls = []

#     for url in urls[:MAX_URLS]:
#         normalized = _normalize_url(url)
#         if normalized and normalized not in valid_urls:
#             valid_urls.append(normalized)
#         elif url.strip():
#             invalid_urls.append(url.strip())

#     return valid_urls, invalid_urls


# def validate_citations(report, source_summaries):
#     valid_labels = {source["label"] for source in source_summaries}
#     cited_labels = set(CITATION_PATTERN.findall(report or ""))
#     unknown_labels = sorted(label for label in cited_labels if label not in valid_labels)
#     has_any_citation = bool(cited_labels)
#     return {
#         "has_any_citation": has_any_citation,
#         "cited_labels": sorted(cited_labels),
#         "unknown_labels": unknown_labels,
#     }


# def plan_research(topic, client):
#     fallback = {
#         "goal": topic,
#         "sub_questions": [
#             f"What is the main claim about {topic}?",
#             f"What evidence supports or challenges {topic}?",
#             f"What should the reader watch out for when evaluating {topic}?",
#         ],
#         "report_sections": ["Overview", "Key Findings", "Risks", "Conclusion"],
#     }
#     return _chat_json(
#         client,
#         "You create concise research plans. Return JSON with goal, sub_questions, and report_sections.",
#         f"Topic: {topic}\nReturn a focused research plan with at most 5 sub-questions.",
#         fallback,
#     )


# def _normalize_url(url):
#     parsed = urlparse(url.strip())
#     if parsed.scheme in {"http", "https"} and parsed.netloc:
#         return url.strip()
#     return None


# def fetch_source(url):
#     article = Article(url)
#     article.download()
#     article.parse()
#     text = (article.text or "").strip()
#     title = (article.title or url).strip()
#     if not text:
#         raise ValueError("Could not extract article text from the URL.")
#     return {
#         "url": url,
#         "title": title,
#         "text": text[:MAX_SOURCE_CHARS],
#     }


# def summarize_source(source, topic, plan, client, label):
#     fallback = {
#         "label": label,
#         "title": source["title"],
#         "summary": source["text"][:800],
#         "key_points": [],
#         "relevance": "Relevant to the topic.",
#     }
#     summary = _chat_json(
#         client,
#         "You summarize research sources. Return JSON with label, title, summary, key_points, and relevance.",
#         (
#             f"Research topic: {topic}\n"
#             f"Plan sub-questions: {json.dumps(plan.get('sub_questions', []))}\n"
#             f"Source label: {label}\n"
#             f"Source title: {source['title']}\n"
#             f"Source URL: {source['url']}\n"
#             f"Source text:\n{source['text']}"
#         ),
#         fallback,
#     )
#     summary["url"] = source["url"]
#     summary["title"] = source["title"]
#     return summary


# def synthesize_report(topic, plan, source_summaries, client):
#     source_payload = [
#         {
#             "label": source["label"],
#             "title": source["title"],
#             "url": source["url"],
#             "summary": source["summary"],
#             "key_points": source.get("key_points", []),
#             "relevance": source.get("relevance", ""),
#         }
#         for source in source_summaries
#     ]
#     return _chat_text(
#         client,
#         (
#             "You write grounded research reports in Markdown. "
#             "Use only the provided sources. Every substantive claim must cite one or more source labels like [S1]. "
#             "If evidence is limited or conflicting, say so clearly."
#         ),
#         (
#             f"Research topic: {topic}\n"
#             f"Plan: {json.dumps(plan)}\n"
#             f"Sources: {json.dumps(source_payload)}\n\n"
#             "Write a concise report with these sections:\n"
#             "1. Executive Summary\n"
#             "2. Findings\n"
#             "3. Risks and Gaps\n"
#             "4. Recommended Next Questions\n"
#             "5. Source List\n"
#         ),
#     )


# def critique_report(topic, source_summaries, report, client):
#     fallback = {
#         "passes_review": True,
#         "issues": [],
#         "revised_report": report,
#     }
#     critique = _chat_json(
#         client,
#         (
#             "You are a research quality reviewer. Return JSON with passes_review, issues, and revised_report. "
#             "Mark passes_review false if the report contains unsupported claims, weak sourcing, or misses major caveats."
#         ),
#         (
#             f"Topic: {topic}\n"
#             f"Sources: {json.dumps(source_summaries)}\n"
#             f"Draft report:\n{report}"
#         ),
#         fallback,
#     )
#     if not critique.get("revised_report"):
#         critique["revised_report"] = report
#     return critique


# def revise_report(topic, plan, source_summaries, report, critique, client):
#     return _chat_text(
#         client,
#         (
#             "You revise research reports. Use only the provided sources. "
#             "Every substantive claim must include valid source labels like [S1]. "
#             "Do not invent citations. Fix grounding or completeness issues from the critique."
#         ),
#         (
#             f"Topic: {topic}\n"
#             f"Plan: {json.dumps(plan)}\n"
#             f"Sources: {json.dumps(source_summaries)}\n"
#             f"Critique: {json.dumps(critique)}\n"
#             f"Draft report:\n{report}"
#         ),
#     )


# def run_research_agent(topic, urls, api_key):
#     client = OpenAI(api_key=api_key)
#     plan = plan_research(topic, client)
#     valid_urls, invalid_urls = validate_urls(urls)
#     if not valid_urls:
#         raise ValueError("Please provide at least one valid research URL.")

#     source_summaries = []
#     source_errors = []

#     for index, url in enumerate(valid_urls, start=1):
#         label = f"S{index}"
#         try:
#             source = fetch_source(url)
#             source_summary = summarize_source(source, topic, plan, client, label)
#             source_summaries.append(source_summary)
#         except Exception as exc:
#             source_errors.append({"label": label, "url": url, "error": str(exc)})

#     if not source_summaries:
#         raise ValueError("The Research Agent could not process any of the provided URLs.")

#     draft_report = synthesize_report(topic, plan, source_summaries, client)
#     critique = critique_report(topic, source_summaries, draft_report, client)
#     final_report = critique.get("revised_report", draft_report)
#     citation_check = validate_citations(final_report, source_summaries)

#     needs_revision = (
#         not critique.get("passes_review", False)
#         or not citation_check["has_any_citation"]
#         or bool(citation_check["unknown_labels"])
#     )

#     if needs_revision:
#         final_report = revise_report(topic, plan, source_summaries, final_report, critique, client)
#         critique = critique_report(topic, source_summaries, final_report, client)
#         citation_check = validate_citations(final_report, source_summaries)

#     return {
#         "plan": plan,
#         "sources": source_summaries,
#         "source_errors": source_errors,
#         "invalid_urls": invalid_urls,
#         "draft_report": draft_report,
#         "final_report": final_report,
#         "critique": critique,
#         "citation_check": citation_check,
#     }


# def show_research_agent(api_key=None):
#     st.subheader("Research Agent")
#     st.caption("Planner -> source reader -> source summarizer -> synthesis -> critique")

#     if not api_key:
#         st.error("OpenAI API key is required for the Research Agent.")
#         return

#     topic = st.text_area(
#         "Research topic",
#         placeholder="Example: Evaluate the recent progress and risks of small language models for enterprise support bots.",
#         height=100,
#     )

#     st.markdown("### Source URLs")
#     urls = []
#     for index in range(5):
#         urls.append(st.text_input(f"URL {index + 1}", key=f"research_agent_url_{index}"))

#     if "research_agent_result" not in st.session_state:
#         st.session_state.research_agent_result = None

#     if st.button("Run Research Agent", type="primary"):
#         if not topic.strip():
#             st.warning("Please enter a research topic before running the agent.")
#             return

#         with st.spinner("Planning, reading sources, and drafting the report..."):
#             try:
#                 result = run_research_agent(topic.strip(), urls, api_key)
#             except Exception as exc:
#                 st.error(f"Research Agent failed: {exc}")
#                 return
#         st.session_state.research_agent_result = result

#     result = st.session_state.research_agent_result
#     if not result:
#         return

#     st.markdown("### Research Plan")
#     st.json(result["plan"])

#     if result["invalid_urls"]:
#         st.markdown("### Ignored URLs")
#         for item in result["invalid_urls"]:
#             st.warning(f"Invalid URL skipped: {item}")

#     st.markdown("### Source Digests")
#     for source in result["sources"]:
#         with st.expander(f"{source['label']} - {source['title']}"):
#             st.markdown(f"**URL:** {source['url']}")
#             st.markdown(f"**Summary:** {source['summary']}")
#             points = source.get("key_points", [])
#             if points:
#                 st.markdown("**Key Points**")
#                 for point in points:
#                     st.write(f"- {point}")
#             st.markdown(f"**Relevance:** {source.get('relevance', 'N/A')}")

#     if result["source_errors"]:
#         st.markdown("### Source Errors")
#         for item in result["source_errors"]:
#             st.warning(f"{item['label']} ({item['url']}): {item['error']}")

#     st.markdown("### Critique")
#     critique = result["critique"]
#     st.write(f"Passes review: {'Yes' if critique.get('passes_review') else 'No'}")
#     issues = critique.get("issues", [])
#     if issues:
#         for issue in issues:
#             st.write(f"- {issue}")
#     else:
#         st.write("No major grounding issues were flagged.")

#     st.markdown("### Citation Check")
#     citation_check = result["citation_check"]
#     st.write(f"Has citations: {'Yes' if citation_check['has_any_citation'] else 'No'}")
#     st.write(f"Cited labels: {', '.join(citation_check['cited_labels']) if citation_check['cited_labels'] else 'None'}")
#     if citation_check["unknown_labels"]:
#         st.error(f"Unknown citation labels found: {', '.join(citation_check['unknown_labels'])}")

#     st.markdown("### Final Report")
#     st.markdown(result["final_report"])































import json
import re
from urllib.parse import urlparse

import streamlit as st
from newspaper import Article
from openai import OpenAI

# --- Configuration ---
MODEL_NAME = "gpt-4o-mini"
MAX_URLS = 5
MAX_SOURCE_CHARS = 12000
CITATION_PATTERN = re.compile(r"\[(S\d+)\]")

# --- Helper Functions ---

def _strip_code_fences(value):
    """Removes markdown code fences from LLM responses."""
    if not isinstance(value, str):
        value = str(value)
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
    """Safely loads JSON from LLM response."""
    try:
        return json.loads(_strip_code_fences(value))
    except (json.JSONDecodeError, TypeError):
        return fallback


def _chat_json(client, system_prompt, user_prompt, fallback):
    """Calls LLM for JSON output with fallback."""
    try:
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
    except Exception:
        return fallback


def _chat_text(client, system_prompt, user_prompt):
    """Calls LLM for text output."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception:
        return ""


# --- Core Logic ---

def validate_urls(urls):
    valid_urls = []
    invalid_urls = []

    for url in urls[:MAX_URLS]:
        normalized = _normalize_url(url)
        if normalized and normalized not in valid_urls:
            valid_urls.append(normalized)
        elif url.strip():
            invalid_urls.append(url.strip())

    return valid_urls, invalid_urls


def validate_citations(report, source_summaries):
    """
    FIX: Ensures report is a string before regex processing.
    """
    # Type Safety: Convert dict to string if necessary
    if isinstance(report, dict):
        report = report.get("revised_report", str(report))
    elif not isinstance(report, str):
        report = str(report)

    valid_labels = {source["label"] for source in source_summaries}
    cited_labels = set(CITATION_PATTERN.findall(report or ""))
    unknown_labels = sorted(label for label in cited_labels if label not in valid_labels)
    has_any_citation = bool(cited_labels)
    
    return {
        "has_any_citation": has_any_citation,
        "cited_labels": sorted(cited_labels),
        "unknown_labels": unknown_labels,
    }


def plan_research(topic, client):
    fallback = {
        "goal": topic,
        "sub_questions": [
            f"What is the main claim about {topic}?",
            f"What evidence supports or challenges {topic}?",
            f"What should the reader watch out for when evaluating {topic}?",
        ],
        "report_sections": ["Overview", "Key Findings", "Risks", "Conclusion"],
    }
    return _chat_json(
        client,
        "You create concise research plans. Return JSON with goal, sub_questions, and report_sections.",
        f"Topic: {topic}\nReturn a focused research plan with at most 5 sub-questions.",
        fallback,
    )


def _normalize_url(url):
    parsed = urlparse(url.strip())
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url.strip()
    return None


def fetch_source(url):
    article = Article(url)
    article.download()
    article.parse()
    text = (article.text or "").strip()
    title = (article.title or url).strip()
    if not text:
        raise ValueError("Could not extract article text from the URL.")
    return {
        "url": url,
        "title": title,
        "text": text[:MAX_SOURCE_CHARS],
    }


def summarize_source(source, topic, plan, client, label):
    fallback = {
        "label": label,
        "title": source["title"],
        "summary": source["text"][:800],
        "key_points": [],
        "relevance": "Relevant to the topic.",
    }
    summary = _chat_json(
        client,
        "You summarize research sources. Return JSON with label, title, summary, key_points, and relevance.",
        (
            f"Research topic: {topic}\n"
            f"Plan sub-questions: {json.dumps(plan.get('sub_questions', []))}\n"
            f"Source label: {label}\n"
            f"Source title: {source['title']}\n"
            f"Source URL: {source['url']}\n"
            f"Source text:\n{source['text']}"
        ),
        fallback,
    )
    summary["url"] = source["url"]
    summary["title"] = source["title"]
    return summary


def synthesize_report(topic, plan, source_summaries, client):
    source_payload = [
        {
            "label": source["label"],
            "title": source["title"],
            "url": source["url"],
            "summary": source["summary"],
            "key_points": source.get("key_points", []),
            "relevance": source.get("relevance", ""),
        }
        for source in source_summaries
    ]
    return _chat_text(
        client,
        (
            "You write grounded research reports in Markdown. "
            "Use only the provided sources. Every substantive claim must cite one or more source labels like [S1]. "
            "If evidence is limited or conflicting, say so clearly."
        ),
        (
            f"Research topic: {topic}\n"
            f"Plan: {json.dumps(plan)}\n"
            f"Sources: {json.dumps(source_payload)}\n\n"
            "Write a concise report with these sections:\n"
            "1. Executive Summary\n"
            "2. Findings\n"
            "3. Risks and Gaps\n"
            "4. Recommended Next Questions\n"
            "5. Source List\n"
        ),
    )


def critique_report(topic, source_summaries, report, client):
    """
    FIX: Ensures revised_report extracted from JSON is a string.
    """
    fallback = {
        "passes_review": True,
        "issues": [],
        "revised_report": report, # Fallback to original report string
    }
    critique = _chat_json(
        client,
        (
            "You are a research quality reviewer. Return JSON with passes_review, issues, and revised_report. "
            "Mark passes_review false if the report contains unsupported claims, weak sourcing, or misses major caveats. "
            "IMPORTANT: 'revised_report' must be a plain STRING, not a nested JSON object."
        ),
        (
            f"Topic: {topic}\n"
            f"Sources: {json.dumps(source_summaries)}\n"
            f"Draft report:\n{report}"
        ),
        fallback,
    )
    
    # Type Safety: Ensure revised_report is a string
    revised = critique.get("revised_report", report)
    if isinstance(revised, dict):
        # If LLM nested it again, try to extract string or fallback
        revised = revised.get("content", report) 
    if not isinstance(revised, str):
        revised = report
        
    critique["revised_report"] = revised
    return critique


def revise_report(topic, plan, source_summaries, report, critique, client):
    return _chat_text(
        client,
        (
            "You revise research reports. Use only the provided sources. "
            "Every substantive claim must include valid source labels like [S1]. "
            "Do not invent citations. Fix grounding or completeness issues from the critique."
        ),
        (
            f"Topic: {topic}\n"
            f"Plan: {json.dumps(plan)}\n"
            f"Sources: {json.dumps(source_summaries)}\n"
            f"Critique: {json.dumps(critique)}\n"
            f"Draft report:\n{report}"
        ),
    )


def run_research_agent(topic, urls, api_key):
    client = OpenAI(api_key=api_key)
    plan = plan_research(topic, client)
    valid_urls, invalid_urls = validate_urls(urls)
    if not valid_urls:
        raise ValueError("Please provide at least one valid research URL.")

    source_summaries = []
    source_errors = []

    for index, url in enumerate(valid_urls, start=1):
        label = f"S{index}"
        try:
            source = fetch_source(url)
            source_summary = summarize_source(source, topic, plan, client, label)
            source_summaries.append(source_summary)
        except Exception as exc:
            source_errors.append({"label": label, "url": url, "error": str(exc)})

    if not source_summaries:
        raise ValueError("The Research Agent could not process any of the provided URLs.")

    # 1. Draft Report (String)
    draft_report = synthesize_report(topic, plan, source_summaries, client)
    
    # 2. Critique (Dict)
    critique = critique_report(topic, source_summaries, draft_report, client)
    
    # 3. Extract Final Report (Ensure String)
    final_report = critique.get("revised_report", draft_report)
    if not isinstance(final_report, str):
        final_report = draft_report  # Fallback to draft if extraction fails

    # 4. Validate Citations
    citation_check = validate_citations(final_report, source_summaries)

    # 5. Check if Revision Needed
    needs_revision = (
        not critique.get("passes_review", False)
        or not citation_check["has_any_citation"]
        or bool(citation_check["unknown_labels"])
    )

    if needs_revision:
        # Revise (Returns String)
        final_report = revise_report(topic, plan, source_summaries, final_report, critique, client)
        
        # Critique Again (Returns Dict)
        critique = critique_report(topic, source_summaries, final_report, client)
        
        # Extract Again (Ensure String)
        revised_version = critique.get("revised_report", final_report)
        if isinstance(revised_version, str):
            final_report = revised_version
            
        # Validate Again
        citation_check = validate_citations(final_report, source_summaries)

    return {
        "plan": plan,
        "sources": source_summaries,
        "source_errors": source_errors,
        "invalid_urls": invalid_urls,
        "draft_report": draft_report,
        "final_report": final_report,
        "critique": critique,
        "citation_check": citation_check,
    }


# --- Streamlit UI ---

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
        urls.append(st.text_input(f"URL {index + 1}", key=f"research_agent_url_{index}"))

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
    st.write(f"Cited labels: {', '.join(citation_check['cited_labels']) if citation_check['cited_labels'] else 'None'}")
    if citation_check["unknown_labels"]:
        st.error(f"Unknown citation labels found: {', '.join(citation_check['unknown_labels'])}")

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
        st.markdown("[LinkedIn](https://www.linkedin.com/in/archit-kumar-aa6375259) | [GitHub](https://github.com/)")

    show_research_agent(api_key)


if __name__ == "__main__":
    main()
