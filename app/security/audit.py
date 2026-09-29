from app.utils.logger import logger


def log_security_event(
    event_type: str,
    owner_id: int,
    action: str,
    result: str,
    request_id: str | None = None,
    finding_count: int = 0,
) -> None:
    """
    Log a security event without exposing sensitive content.
    """

    logger.warning(
        "Security audit | "
        "event_type=%s | "
        "owner_id=%s | "
        "request_id=%s | "
        "action=%s | "
        "result=%s | "
        "finding_count=%s",
        event_type,
        owner_id,
        request_id,
        action,
        result,
        finding_count,
    )