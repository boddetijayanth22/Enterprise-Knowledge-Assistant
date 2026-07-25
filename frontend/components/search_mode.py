import streamlit as st

def render_search_mode():

    st.markdown("## ⚙ Retrieval")

    MODE_MAP = {
        "Semantic": "semantic",
        "BM25": "bm25",
        "Hybrid": "hybrid",
        "Hybrid + Re-ranker": "hybrid_reranker",
    }

    mode = st.radio(
        "Select Retrieval Strategy",
        options=list(MODE_MAP.keys()),
        key = "selected_mode",
    )

    st.session_state.search_mode = MODE_MAP[mode]

    st.divider()