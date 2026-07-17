import retrieve

def tokenize(text: str) -> list[str]:
    """
    Tokenize text for BM25 retrieval.
    """

    text = text.lower()

    text = re.sub(r"[^\w\s]", "", text)

    return text.split()