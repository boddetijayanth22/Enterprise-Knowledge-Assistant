from enum import Enum

from app.privacy.classifier import DataClassification


class PrivacyAction(str, Enum):
    ALLOW = "ALLOW"
    REDACT = "REDACT"
    BLOCK = "BLOCK"


def evaluate_policy(
    classification: DataClassification | str,
    has_sensitive_data: bool,
) -> PrivacyAction:

    if isinstance(classification, str):
        classification = DataClassification(classification.upper())

    if classification == DataClassification.RESTRICTED:
        return PrivacyAction.BLOCK

    if has_sensitive_data:
        return PrivacyAction.REDACT

    return PrivacyAction.ALLOW