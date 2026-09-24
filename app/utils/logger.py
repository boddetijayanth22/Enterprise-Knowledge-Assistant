import logging

from app.config.settings import settings


def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )


logger = logging.getLogger("Enterprise-RAG")