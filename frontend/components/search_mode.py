import streamlit as st


def render_search_mode():

    st.markdown("## ⚙ Retrieval")

    st.success(
        "🟢 Active: Semantic Search"
    )

    st.info(
        """
🚧 Hybrid Search

Coming in Version 2
"""
    )

    st.divider()