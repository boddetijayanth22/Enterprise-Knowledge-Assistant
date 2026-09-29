import re


RETRIEVAL_INJECTION_PATTERNS = [
    re.compile(
        r"\bignore\s+(all\s+)?previous\s+instructions\b",
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
        r"\bdeveloper\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bhidden\s+instructions\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bexfiltrate\b.*\b(secret|credential|password|api\s*key)\b",
        re.IGNORECASE,
    ),
]


def detect_retrieval_injection(text: str) -> dict:
    findings = []

    for pattern in RETRIEVAL_INJECTION_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)

    return {
        "is_injection": bool(findings),
        "findings": findings,
    }