from app.security.output_guard import (
    detect_secret_leakage,
    redact_secret_leakage,
)


def run_detection_test(name, text, expected):
    result = detect_secret_leakage(text)

    assert result["has_secret"] == expected, (
        f"{name} failed: {result}"
    )

    print(f"PASS: {name}")


def run_redaction_test(name, text, expected_text):
    result = redact_secret_leakage(text)

    assert result == expected_text, (
        f"{name} failed: {result}"
    )

    print(f"PASS: {name}")


run_detection_test(
    "Normal response",
    "Machine learning uses training data to learn patterns.",
    False,
)

run_detection_test(
    "API key detection",
    "API key: sk-abcdefghijklmnopqrstuvwxyz",
    True,
)

run_detection_test(
    "Password detection",
    "password: MySecret123",
    True,
)

run_detection_test(
    "Private key detection",
    "-----BEGIN PRIVATE KEY-----",
    True,
)

run_detection_test(
    "JWT detection",
    "Token: eyJhbGciOiJIUzI1NiJ9.abcdefghijklmnop.qrstuvwxyz123456",
    True,
)


run_redaction_test(
    "API key redaction",
    "API key: sk-abcdefghijklmnopqrstuvwxyz",
    "API key: [REDACTED_API_KEY]",
)

run_redaction_test(
    "Password redaction",
    "password: MySecret123",
    "password: [REDACTED_PASSWORD]",
)

run_redaction_test(
    "Private key redaction",
    "-----BEGIN PRIVATE KEY-----",
    "[REDACTED_PRIVATE_KEY]",
)

print("All output guard tests passed.")