from app.cache.query_cache import QueryCache


def test_cache_returns_stored_result():
    cache = QueryCache(ttl_seconds=60)

    result = {
        "answer": "cached answer",
        "sources": [],
    }

    cache.set(
        question="What is RAG?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=1,
        value=result,
    )

    assert cache.get(
        question="What is RAG?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=1,
    ) == result


def test_cache_isolates_users():
    cache = QueryCache(ttl_seconds=60)

    result = {
        "answer": "private answer",
        "sources": [],
    }

    cache.set(
        question="What is RAG?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=1,
        value=result,
    )

    assert cache.get(
        question="What is RAG?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=2,
    ) is None


def test_cache_miss_for_different_query():
    cache = QueryCache(ttl_seconds=60)

    cache.set(
        question="What is RAG?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=1,
        value={"answer": "answer", "sources": []},
    )

    assert cache.get(
        question="What is embeddings?",
        documents=["doc.pdf"],
        mode="semantic",
        owner_id=1,
    ) is None