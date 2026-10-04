import time

from qdrant_client.models import Distance, VectorParams

from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client


MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 2


def initialize_qdrant():
    client = get_qdrant_client()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            if client.collection_exists(settings.collection_name):
                print(
                    f"Qdrant collection '{settings.collection_name}' "
                    "already exists."
                )
                return

            client.create_collection(
                collection_name=settings.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Qdrant collection '{settings.collection_name}' "
                "created successfully."
            )
            return

        except Exception as exc:
            if attempt == MAX_ATTEMPTS:
                raise

            print(
                f"Qdrant unavailable "
                f"(attempt {attempt}/{MAX_ATTEMPTS}): {exc}"
            )
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    initialize_qdrant()