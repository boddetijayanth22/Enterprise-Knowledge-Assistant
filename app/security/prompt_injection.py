import re


INJECTION_PATTERNS = [
    re.compile(
        r"\bignore\s+(all\s+)?previous\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bignore\s+(all\s+)?prior\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bforget\s+(all\s+)?previous\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\breveal\s+(the\s+)?system\s+prompt\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bshow\s+(me\s+)?(the\s+)?system\s+prompt\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bprint\s+(the\s+)?system\s+prompt\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdeveloper\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bhidden\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdo\s+not\s+follow\s+(the\s+)?system\b",
        re.IGNORECASE,
    ),
]


def detect_prompt_injection(text: str) -> dict:
    findings = []

    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)

    return {
        "is_injection": bool(findings),
        "findings": findings,
    }