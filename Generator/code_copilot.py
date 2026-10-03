"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.code_copilot import (
    _strip_code_fences,
    _chat_text,
    generate_initial_code,
    repair_code,
    verify_python_code,
    verify_javascript_code,
    verify_java_code,
    verify_c_family_code,
    verify_code,
    run_code_copilot,
    MODEL_NAME,
    LANGUAGE_CONFIG,
    SUPPORTED_LANGUAGES,
)


def show_code_copilot(api_key=None):
    st.subheader("Code Copilot")
    st.caption(
        "Prompt -> generate -> verify in temp sandbox -> repair once -> final code + report"
    )

    if not api_key:
        st.error("OpenAI API key is required for Code Copilot.")
        return

    language = st.selectbox(
        "Language", SUPPORTED_LANGUAGES, key="code_copilot_language"
    )
    prompt = st.text_area(
        "Describe what the code should do",
        placeholder="Example: Write a Python function that reads a CSV file and returns the top 5 rows sorted by revenue descending.",
        height=140,
        key="code_copilot_prompt",
    )

    if "code_copilot_result" not in st.session_state:
        st.session_state.code_copilot_result = None

    if st.button("Run Code Copilot", type="primary"):
        if not prompt.strip():
            st.warning("Please describe the code task first.")
            return

        with st.spinner("Generating and verifying code..."):
            try:
                result = run_code_copilot(prompt.strip(), api_key, language)
            except Exception as exc:
                st.error(f"Code Copilot failed: {exc}")
                return
        st.session_state.code_copilot_result = result

    result = st.session_state.code_copilot_result
    if not result:
        return

    st.markdown("### Final Verification")
    st.write(f"Passed: {'Yes' if result['final_verification']['passed'] else 'No'}")
    st.json(result["final_verification"])

    unavailable_checks = [
        item
        for item in result["final_verification"]["checks"]
        if "unavailable" in item["details"].lower()
    ]
    if unavailable_checks:
        st.info(
            "Local verification for this language depends on compiler/runtime tools installed on this machine."
        )

    if result["repair_attempted"]:
        st.markdown("### Initial Verification")
        st.json(result["initial_verification"])

    st.markdown("### Final Code")
    st.code(result["final_code"], language=result["language"])
