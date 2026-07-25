SEARCH_MODE = "semantic"

if SEARCH_MODE == "bm25":

    chunks = bm25.retrieve(query)

else:

    chunks = semantic.retrieve(query)