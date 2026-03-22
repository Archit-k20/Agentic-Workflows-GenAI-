import json
import re
from urllib.parse import urlparse

import streamlit as st
from newspaper import Article
from openai import OpenAI


MODEL_NAME = "gpt-4o-mini"
MAX_URLS = 5
MAX_SOURCE_CHARS = 10000


def _strip_code_fences(value):
    cleaned = (value or "").strip()
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


def _normalize_url(url):
    parsed = urlparse(url.strip())
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url.strip()
    return None


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


def fetch_support_source(url):
    article = Article(url)
    article.download()
    article.parse()
    text = (article.text or "").strip()
    title = (article.title or url).strip()
    if not text:
        raise ValueError("Could not extract support content from the URL.")
    return {"url": url, "title": title, "text": text[:MAX_SOURCE_CHARS]}


def classify_intent(question, client):
    fallback = {
        "intent": "general_support",
        "severity": "medium",
        "requires_human": False,
        "reason": "General support request.",
    }
    return _chat_json(
        client,
        (
            "You classify support requests. "
            "Return JSON with intent, severity, requires_human, and reason. "
            "Severity must be low, medium, or high."
        ),
        f"Question: {question}",
        fallback,
    )


def summarize_support_source(question, source, label, client):
    fallback = {
        "label": label,
        "title": source["title"],
        "summary": source["text"][:700],
        "relevance": "Potentially relevant support source.",
    }
    summary = _chat_json(
        client,
        (
            "You summarize support documentation for triage. "
            "Return JSON with label, title, summary, and relevance."
        ),
        (
            f"Support question: {question}\n"
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


def draft_support_resolution(question, intent, source_summaries, client):
    fallback = {
        "resolution_type": "answer",
        "answer": "Based on the provided sources, here is the best available guidance.",
        "confidence": 0.55,
        "escalation_reason": "",
        "recommended_next_step": "Review the cited sources and confirm details.",
    }
    return _chat_json(
        client,
        (
            "You are a support triage agent. "
            "Return JSON with resolution_type, answer, confidence, escalation_reason, and recommended_next_step. "
            "resolution_type must be answer or escalate. "
            "confidence must be between 0 and 1. "
            "Use only the provided sources and cite them inline like [S1]. "
            "Escalate if evidence is weak, conflicting, or the issue is high risk."
        ),
        (
            f"Question: {question}\n"
            f"Intent: {json.dumps(intent)}\n"
            f"Sources: {json.dumps(source_summaries)}"
        ),
        fallback,
    )


def finalize_triage(question, intent, draft, source_summaries):
    valid_labels = {item["label"] for item in source_summaries}
    cited_labels = set(re.findall(r"\[(S\d+)\]", draft.get("answer", "")))
    unknown_labels = sorted(label for label in cited_labels if label not in valid_labels)

    confidence = draft.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    escalate = (
        draft.get("resolution_type") == "escalate"
        or intent.get("requires_human", False)
        or confidence < 0.6
        or bool(unknown_labels)
        or not cited_labels
    )

    if escalate:
        resolution_type = "escalate"
        escalation_reason = draft.get("escalation_reason") or "Confidence was too low or the available evidence was insufficient."
        if unknown_labels:
            escalation_reason = f"{escalation_reason} Invalid citations detected: {', '.join(unknown_labels)}."
        answer = draft.get("answer") or "This request should be escalated for human review."
    else:
        resolution_type = "answer"
        escalation_reason = ""
        answer = draft.get("answer", "")

    return {
        "question": question,
        "intent": intent,
        "resolution_type": resolution_type,
        "answer": answer,
        "confidence": confidence,
        "recommended_next_step": draft.get("recommended_next_step", "No next step provided."),
        "escalation_reason": escalation_reason,
        "citation_check": {
            "cited_labels": sorted(cited_labels),
            "unknown_labels": unknown_labels,
        },
    }


def run_support_triage(question, urls, api_key):
    if not question.strip():
        raise ValueError("Please enter a support question.")

    client = OpenAI(api_key=api_key)
    intent = classify_intent(question, client)
    valid_urls, invalid_urls = validate_urls(urls)

    if not valid_urls:
        raise ValueError("Please provide at least one valid support URL.")

    source_summaries = []
    source_errors = []

    for index, url in enumerate(valid_urls, start=1):
        label = f"S{index}"
        try:
            source = fetch_support_source(url)
            summary = summarize_support_source(question, source, label, client)
            source_summaries.append(summary)
        except Exception as exc:
            source_errors.append({"label": label, "url": url, "error": str(exc)})

    if not source_summaries:
        raise ValueError("The Support/Triage Agent could not process any of the provided support URLs.")

    draft = draft_support_resolution(question, intent, source_summaries, client)
    final = finalize_triage(question, intent, draft, source_summaries)

    return {
        "intent": intent,
        "sources": source_summaries,
        "source_errors": source_errors,
        "invalid_urls": invalid_urls,
        "draft": draft,
        "final": final,
    }


def show_support_triage(api_key=None):
    st.subheader("Support/Triage Agent")
    st.caption("Question -> intent detection -> source retrieval -> grounded answer or escalation")

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
        urls.append(st.text_input(f"Support URL {index + 1}", key=f"support_triage_url_{index}"))

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
