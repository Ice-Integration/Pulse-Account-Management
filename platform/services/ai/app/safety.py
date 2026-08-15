import re

BLOCKED_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"reveal .*system prompt",
    r"developer message",
    r"bypass .*policy",
]


def is_unsafe_prompt(text: str) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in BLOCKED_PATTERNS)
