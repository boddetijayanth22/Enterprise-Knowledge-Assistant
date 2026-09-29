import re


SECRET_PATTERNS = {
    "API_KEY": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{10,}|"
        r"AIza[A-Za-z0-9_-]{20,}|"
        r"AKIA[A-Z0-9]{16})\b"
    ),
    "PASSWORD": re.compile(
        r"(?i)(?P<label>\b(?:password|passwd|pwd)\s*[:=]\s*)\S+"
    ),
    "PRIVATE_KEY": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    ),
    "JWT": re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\."
        r"[A-Za-z0-9_-]{10,}\."
        r"[A-Za-z0-9_-]{10,}\b"
    ),
}


REDACTION_LABELS = {
    "API_KEY": "[REDACTED_API_KEY]",
    "PASSWORD": "[REDACTED_PASSWORD]",
    "PRIVATE_KEY": "[REDACTED_PRIVATE_KEY]",
    "JWT": "[REDACTED_JWT]",
}


def detect_secret_leakage(text: str) -> dict:
    findings = []

    for secret_type, pattern in SECRET_PATTERNS.items():
        matches = pattern.findall(text)

        if matches:
            findings.append(
                {
                    "type": secret_type,
                    "count": len(matches),
                }
            )

    return {
        "has_secret": bool(findings),
        "findings": findings,
    }

def redact_secret_leakage(text: str) -> str:
    redacted_text = text

    for secret_type, pattern in SECRET_PATTERNS.items():
        replacement = REDACTION_LABELS[secret_type]

        if secret_type == "PASSWORD":
            redacted_text = pattern.sub(
                rf"\g<label>{replacement}",
                redacted_text,
            )
        else:
            redacted_text = pattern.sub(
                replacement,
                redacted_text,
            )

    return redacted_text