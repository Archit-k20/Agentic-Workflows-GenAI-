"""Shared workflow logic; prompts and inference settings preserved from the Streamlit application."""

import json

from .runtime import client as OpenAI

from .text_to_speech import generate_speech

MODEL_NAME = "gpt-4o-mini"

TONE_OPTIONS = [
    "professional",
    "playful",
    "educational",
    "launch-ready",
    "social-first",
]

PLATFORM_OPTIONS = ["linkedin", "x", "instagram", "youtube", "blog"]


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
        temperature=0.4,
    )
    content = response.choices[0].message.content or ""
    return _load_json(content, fallback)


def build_content_plan(idea, tone, platforms, client):
    fallback = {
        "content_angle": idea,
        "audience": "General audience",
        "hooks": [f"Why {idea} matters now"],
        "sections": ["Hook", "Main Value", "Call to Action"],
        "cta": "Invite the audience to learn more or engage.",
    }
    return _chat_json(
        client,
        (
            "You design short multimodal content plans. "
            "Return JSON with content_angle, audience, hooks, sections, and cta."
        ),
        (f"Idea: {idea}\nTone: {tone}\nPlatforms: {json.dumps(platforms)}"),
        fallback,
    )


def build_content_package(idea, tone, platforms, plan, client):
    fallback = {
        "title": idea,
        "script": f"{idea}\n\nKey message: explain the idea clearly and end with a call to action.",
        "image_prompts": [f"Create a polished hero visual for: {idea}"],
        "captions": {
            platform: f"{idea} - engaging caption for {platform}."
            for platform in platforms
        },
        "hashtags": ["#AI", "#Content"],
        "cta": plan.get("cta", "Learn more."),
    }
    return _chat_json(
        client,
        (
            "You create multimodal content packages. "
            "Return JSON with title, script, image_prompts, captions, hashtags, and cta. "
            "captions must be an object keyed by platform. "
            "image_prompts should contain 2 to 4 detailed visual prompts."
        ),
        (
            f"Idea: {idea}\n"
            f"Tone: {tone}\n"
            f"Platforms: {json.dumps(platforms)}\n"
            f"Plan: {json.dumps(plan)}"
        ),
        fallback,
    )


def critique_content_package(idea, tone, platforms, plan, package, client):
    fallback = {
        "passes_review": True,
        "issues": [],
        "revised_script": package.get("script", ""),
        "revised_captions": package.get("captions", {}),
    }
    return _chat_json(
        client,
        (
            "You review marketing content packages. "
            "Return JSON with passes_review, issues, revised_script, and revised_captions. "
            "Improve clarity, consistency, and platform fit if needed."
        ),
        (
            f"Idea: {idea}\n"
            f"Tone: {tone}\n"
            f"Platforms: {json.dumps(platforms)}\n"
            f"Plan: {json.dumps(plan)}\n"
            f"Package: {json.dumps(package)}"
        ),
        fallback,
    )


def run_content_pipeline(
    idea,
    tone,
    platforms,
    api_key,
    include_audio=False,
    voice="alloy",
    audio_output_path=None,
):
    if not idea.strip():
        raise ValueError("Please provide a content idea.")
    if not platforms:
        raise ValueError("Please choose at least one target platform.")

    client = OpenAI(api_key=api_key)
    plan = build_content_plan(idea, tone, platforms, client)
    package = build_content_package(idea, tone, platforms, plan, client)
    critique = critique_content_package(idea, tone, platforms, plan, package, client)

    final_script = critique.get("revised_script") or package.get("script", "")
    final_captions = critique.get("revised_captions") or package.get("captions", {})
    audio_path = None
    audio_error = None

    if include_audio and final_script.strip():
        audio_result = generate_speech(
            final_script, voice=voice, api_key=api_key, output_path=audio_output_path
        )
        if isinstance(audio_result, str) and audio_result.startswith("Error"):
            audio_error = audio_result
        else:
            audio_path = audio_result

    return {
        "plan": plan,
        "package": package,
        "critique": critique,
        "final_script": final_script,
        "final_captions": final_captions,
        "audio_path": audio_path,
        "audio_error": audio_error,
    }
