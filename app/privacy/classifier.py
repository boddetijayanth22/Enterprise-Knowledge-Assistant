from enum import Enum


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


DEFAULT_CLASSIFICATION = DataClassification.INTERNAL


def normalize_classification(value: str | None) -> DataClassification:
    if not value:
        return DEFAULT_CLASSIFICATION

    try:
        return DataClassification(value.strip().upper())
    except ValueError:
        raise ValueError(
            f"Unsupported data classification: {value}. "
            f"Allowed values: {[item.value for item in DataClassification]}"
        )