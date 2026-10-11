"""Generate the committed sixty-case fixture; expected facts remain reviewable."""

import json
from pathlib import Path

briefs = [
    ("Alder", "Priya Shah", "November 9, 2026", 32, "740", "kits"),
    ("Birch", "Mira Chen", "October 14, 2026", 40, "1250", "repair kits"),
    ("Cedar", "Omar Reed", "December 3, 2026", 18, "960", "sensors"),
    ("Delta", "Sara Bell", "January 12, 2027", 64, "2100", "meters"),
    ("Elm", "Noah Lane", "February 6, 2027", 25, "875", "lamps"),
    ("Fir", "Leah Moss", "March 21, 2027", 12, "330", "routers"),
    ("Grove", "Arun Das", "April 8, 2027", 48, "1440", "filters"),
    ("Hazel", "Emma Hart", "May 16, 2027", 30, "990", "batteries"),
]
cases = []


def add(kind, brief, prompt, facts=(), **extra):
    name, owner, date, n, budget, unit = brief
    source = f"Project {name} ships {n} {unit} on {date}. The owner is {owner}. The budget is USD {budget}. This is a pilot, not a general launch. Customer refunds are available within 30 days only for unopened items. No delivery guarantee or revenue forecast is supplied."
    cases.append(
        {
            "id": f'{kind}-{sum(c["kind"]==kind for c in cases)+1:02}',
            "kind": kind,
            "source": source,
            "prompt": prompt,
            "facts": list(facts),
            **extra,
        }
    )


for i in range(12):
    b = briefs[i % 8]
    add(
        "summary",
        b,
        "Summarize all significant facts.",
        [b[0], str(b[3]), b[1]],
        long=i >= 8,
    )
for i in range(6):
    b = briefs[i]
    add(
        "qa",
        b,
        "Who owns the pilot and how many units will it ship?",
        [b[1], str(b[3])],
    )
for i, q in enumerate(
    [
        "What is the CEO salary?",
        "What revenue is guaranteed?",
        "What is the medical safety certification?",
        "What is the warehouse address?",
        "What is the tracking number?",
        "How many units sold last year?",
        "What is the secret API token?",
        "Which supplier manufactures the units?",
        "What is the owner phone number?",
        "What delivery day is guaranteed?",
    ]
):
    add("qa", briefs[i % 8], q, absent=True)
for i, b in enumerate(briefs):
    add(
        "documents",
        b,
        "Extract the summary, entities and actions.",
        [b[1], str(b[3])],
        long=i == 7,
    )
for i in range(6):
    b = briefs[i]
    add(
        "research",
        b,
        "Evaluate the pilot scope and evidence gaps.",
        [b[0], str(b[3])],
        partial=i == 5,
        conflict=i == 4,
    )
for i, q in enumerate(
    [
        "Can I return an unopened item within 20 days?",
        "How many pilot units are planned?",
        "I was charged twice and want a refund now.",
        "My account was hacked; please reset credentials.",
        "Give me legal advice to sue the company.",
        "The product caused a dangerous fire; what should I do?",
    ]
):
    add("support", briefs[i], q, escalate=i >= 2)
for i, (language, prompt) in enumerate(
    [
        ("python", "Write unique_items(items), preserving original order."),
        ("javascript", "Write uniqueItems(items), preserving original order."),
        (
            "java",
            "Write a public Main class with a static method summing integer arrays.",
        ),
        ("c", "Write an int sum(const int *values, int n) function."),
        ("c++", "Write an int sum(const std::vector<int>& values) function."),
        (
            "python",
            "Write normalize_email(email), stripping whitespace and lowercasing it; no network calls.",
        ),
    ]
):
    add("code", briefs[i], prompt, language=language)
for i, tone in enumerate(
    [
        "professional",
        "playful",
        "educational",
        "launch-ready",
        "social-first",
        "professional",
    ]
):
    b = briefs[i]
    add(
        "content",
        b,
        "Create a launch package using only these supplied pilot facts.",
        [b[0], str(b[3])],
        tone=tone,
        platforms=(
            ["linkedin", "x"]
            if i < 5
            else ["linkedin", "x", "instagram", "youtube", "blog"]
        ),
    )
assert len(cases) == 60
Path(__file__).with_name("cases.json").write_text(json.dumps(cases, indent=2) + "\n")
