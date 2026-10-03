"""Validate the structured shapes consumed by preserved workflows."""

import json
import re

PROFILES = [
    (
        "goal, sub_questions",
        {"goal": str, "sub_questions": list, "report_sections": list},
    ),
    (
        "key_points",
        {
            "label": str,
            "title": str,
            "summary": str,
            "key_points": list,
            "relevance": str,
        },
    ),
    ("passes_review", {"passes_review": bool, "issues": list}),
    (
        "content_angle",
        {
            "content_angle": str,
            "audience": str,
            "hooks": list,
            "sections": list,
            "cta": str,
        },
    ),
    (
        "image_prompts",
        {
            "title": str,
            "script": str,
            "image_prompts": list,
            "captions": dict,
            "hashtags": list,
            "cta": str,
        },
    ),
    (
        "document_type",
        {
            "document_type": str,
            "summary": str,
            "entities": dict,
            "action_items": list,
            "risks": list,
        },
    ),
    (
        "requires_human",
        {"intent": str, "severity": str, "requires_human": bool, "reason": str},
    ),
    (
        "resolution_type",
        {
            "resolution_type": str,
            "answer": str,
            "confidence": (int, float),
            "escalation_reason": str,
            "recommended_next_step": str,
        },
    ),
    (
        "label, title, summary",
        {"label": str, "title": str, "summary": str, "relevance": str},
    ),
]


def shape_hint(system, platforms=()):
    fields = next((f for marker, f in PROFILES if marker in system), {})
    example = {
        name: (
            ""
            if kind is str
            else (
                False
                if kind is bool
                else ["text"] if kind is list else {} if kind is dict else 0.0
            )
        )
        for name, kind in fields.items()
    }
    if "entities" in fields:
        example["entities"] = {
            key: ["text"] for key in ("people", "organizations", "emails", "dates")
        }
        example["action_items"] = [
            {key: "" for key in ("task", "owner", "due_date", "priority")}
        ]
    if "captions" in fields:
        example["captions"] = (
            {platform: "caption text" for platform in platforms}
            if platforms
            else {"platform": "caption text"}
        )
    if "passes_review" in fields:
        if "revised_report" in system:
            example["revised_report"] = ""
        else:
            example.update(
                revised_script="",
                revised_captions=(
                    {platform: "caption text" for platform in platforms}
                    if platforms
                    else {"platform": "caption text"}
                ),
            )
    return (
        "Return exactly one object with these field TYPES (example values are only a shape, not facts): "
        + json.dumps(example)
        + ". Use empty strings/lists for unknown values, never null, nested section objects, or invented owners/dates. Every list except action_items contains strings."
    )


def validate(content, system, platforms=()):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    value = json.loads(cleaned)
    if not isinstance(value, dict):
        raise ValueError("Expected a structured object.")
    fields = next((f for marker, f in PROFILES if marker in system), {})
    for name, kind in fields.items():
        if name not in value or not isinstance(value[name], kind):
            raise ValueError(f"Invalid structured field: {name}")
        if (
            kind is list
            and name != "action_items"
            and not all(isinstance(x, str) for x in value[name])
        ):
            raise ValueError(f"Expected text items in {name}")
    if "passes_review" in fields:
        field = "revised_report" if "revised_report" in system else "revised_script"
        if not isinstance(value.get(field), str):
            raise ValueError(f"Missing {field}")
        if field == "revised_script" and (
            not isinstance(value.get("revised_captions"), dict)
            or not all(isinstance(v, str) for v in value["revised_captions"].values())
        ):
            raise ValueError("Missing revised captions")
    if "entities" in fields:
        for key in ("people", "organizations", "emails", "dates"):
            if not isinstance(value["entities"].get(key), list) or not all(
                isinstance(v, str) for v in value["entities"][key]
            ):
                raise ValueError("Invalid entities")
        for item in value["action_items"]:
            if not isinstance(item, dict) or not all(
                isinstance(item.get(k), str)
                for k in ("task", "owner", "due_date", "priority")
            ):
                raise ValueError("Invalid action item")
    if "captions" in fields and not all(
        isinstance(v, str) for v in value["captions"].values()
    ):
        raise ValueError("Invalid captions")
    caption_field = (
        "captions"
        if "captions" in fields
        else (
            "revised_captions"
            if "passes_review" in fields and "revised_report" not in system
            else None
        )
    )
    if caption_field and platforms and set(value[caption_field]) != set(platforms):
        raise ValueError("Caption platforms must match every requested platform.")
    if "severity" in fields and value["severity"] not in {"low", "medium", "high"}:
        raise ValueError("Invalid severity")
    if "confidence" in fields and (
        isinstance(value["confidence"], bool)
        or not 0 <= value["confidence"] <= 1
        or value["resolution_type"] not in {"answer", "escalate"}
    ):
        raise ValueError("Invalid support decision")
    return json.dumps(value, ensure_ascii=False)


def schema_for(system, platforms=()):
    """Decoder constraints use the same fields as validation, including nested types."""
    fields = next((f for marker, f in PROFILES if marker in system), {})

    def obj(properties):
        return {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": False,
        }

    string = {"type": "string"}
    strings = {"type": "array", "items": string}
    properties = {
        name: (
            string
            if kind is str
            else (
                {"type": "boolean"}
                if kind is bool
                else (
                    strings
                    if kind is list
                    else {"type": "object"} if kind is dict else {"type": "number"}
                )
            )
        )
        for name, kind in fields.items()
    }
    if "entities" in fields:
        properties["entities"] = obj(
            {key: strings for key in ("people", "organizations", "emails", "dates")}
        )
        properties["action_items"] = {
            "type": "array",
            "items": obj(
                {key: string for key in ("task", "owner", "due_date", "priority")}
            ),
        }
    captions = (
        obj({platform: string for platform in platforms})
        if platforms
        else {"type": "object", "additionalProperties": string}
    )
    if "captions" in fields:
        properties["captions"] = captions
    if "passes_review" in fields:
        if "revised_report" in system:
            properties["revised_report"] = string
        else:
            properties.update(revised_script=string, revised_captions=captions)
    if "severity" in fields:
        properties["severity"] = {"type": "string", "enum": ["low", "medium", "high"]}
    if "confidence" in fields:
        properties["confidence"] = {"type": "number", "minimum": 0, "maximum": 1}
        properties["resolution_type"] = {
            "type": "string",
            "enum": ["answer", "escalate"],
        }
    return obj(properties) if properties else {"type": "object"}
