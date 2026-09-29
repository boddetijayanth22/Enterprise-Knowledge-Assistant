from app.privacy.detector import PATTERNS


REDACTION_LABELS = {
    "EMAIL": "[REDACTED_EMAIL]",
    "PHONE": "[REDACTED_PHONE]",
    "API_KEY": "[REDACTED_API_KEY]",
    "PASSWORD": "[REDACTED_PASSWORD]",
    "PRIVATE_KEY": "[REDACTED_PRIVATE_KEY]",
}


def redact_sensitive_data(text: str) -> str:
    redacted_text = text

    for data_type, pattern in PATTERNS.items():
        replacement = REDACTION_LABELS[data_type]
        redacted_text = pattern.sub(replacement, redacted_text)

    return redacted_text