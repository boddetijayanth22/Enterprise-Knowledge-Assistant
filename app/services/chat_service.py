from app.retrieval.retriever import retrieve
from app.utils.logger import logger


def chat(question: str):

    documents = retrieve(question)

    logger.info("\nTop Retrieved Chunks\n")

    for i, doc in enumerate(documents, start=1):

        logger.info("=" * 60)

        logger.info(f"Result {i}")

        logger.info(f"Score : {doc.metadata['score']:.4f}")

        logger.info(f"Page  : {doc.metadata['page']}")

        logger.info(doc.page_content[:300])

        logger.info()