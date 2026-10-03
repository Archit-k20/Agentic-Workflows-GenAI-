"""Legacy Streamlit presentation. Shared implementation lives in workflows."""

import streamlit as st
from workflows.content_pipeline import (
    _strip_code_fences,
    _load_json,
    _chat_json,
    build_content_plan,
    build_content_package,
    critique_content_package,
    run_content_pipeline,
    MODEL_NAME,
    TONE_OPTIONS,
    PLATFORM_OPTIONS,
)


def show_content_pipeline(api_key=None):
    st.subheader("Multimodal Content Pipeline")
    st.caption(
        "Idea -> content plan -> script -> image prompts -> platform captions -> optional narration"
    )

    if not api_key:
        st.error("OpenAI API key is required for the Content Pipeline.")
        return

    idea = st.text_area(
        "Content idea",
        placeholder="Example: Launch post for an AI assistant that summarizes research reports and extracts action items from documents.",
        height=120,
        key="content_pipeline_idea",
    )
    tone = st.selectbox("Tone", TONE_OPTIONS, key="content_pipeline_tone")
    platforms = st.multiselect(
        "Target platforms",
        PLATFORM_OPTIONS,
        default=["linkedin", "x"],
        key="content_pipeline_platforms",
    )
    include_audio = st.checkbox(
        "Generate narration audio", key="content_pipeline_audio"
    )
    voice = st.selectbox(
        "Narration voice",
        ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        key="content_pipeline_voice",
    )

    if "content_pipeline_result" not in st.session_state:
        st.session_state.content_pipeline_result = None

    if st.button("Run Content Pipeline", type="primary"):
        with st.spinner("Planning and packaging content..."):
            try:
                result = run_content_pipeline(
                    idea=idea.strip(),
                    tone=tone,
                    platforms=platforms,
                    api_key=api_key,
                    include_audio=include_audio,
                    voice=voice,
                )
            except Exception as exc:
                st.error(f"Content Pipeline failed: {exc}")
                return
        st.session_state.content_pipeline_result = result

    result = st.session_state.content_pipeline_result
    if not result:
        return

    st.markdown("### Content Plan")
    st.json(result["plan"])

    st.markdown("### Final Script")
    st.text_area(
        "Script",
        value=result["final_script"],
        height=260,
        key="content_pipeline_script_output",
    )

    st.markdown("### Image Prompts")
    for prompt in result["package"].get("image_prompts", []):
        st.write(f"- {prompt}")

    st.markdown("### Captions")
    st.json(result["final_captions"])

    st.markdown("### Hashtags")
    hashtags = result["package"].get("hashtags", [])
    if hashtags:
        st.write(" ".join(hashtags))
    else:
        st.write("No hashtags generated.")

    st.markdown("### Review")
    critique = result["critique"]
    st.write(f"Passes review: {'Yes' if critique.get('passes_review') else 'No'}")
    issues = critique.get("issues", [])
    if issues:
        for issue in issues:
            st.write(f"- {issue}")
    else:
        st.write("No major content issues were flagged.")

    if result["audio_path"]:
        st.markdown("### Narration")
        st.audio(result["audio_path"], format="audio/mp3")
    elif result["audio_error"]:
        st.warning(result["audio_error"])
