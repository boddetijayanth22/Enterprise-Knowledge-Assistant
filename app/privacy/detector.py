import re


PATTERNS = {
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "PHONE": re.compile(
        r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)"
    ),

    "API_KEY": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{10,}|"
        r"AIza[A-Za-z0-9_-]{20,}|"
        r"AKIA[A-Z0-9]{16})\b"
    ),

    "PASSWORD": re.compile(
        r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*\S+"
    ),

    "PRIVATE_KEY": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    ),
}


def detect_sensitive_data(text: str) -> dict:
    findings = []

    for data_type, pattern in PATTERNS.items():
        matches = pattern.findall(text)

        if matches:
            findings.append(
                {
                    "type": data_type,
                    "count": len(matches),
                }
            )

    return {
        "has_sensitive_data": bool(findings),
        "findings": findings,
    }