import streamlit as st

from api import get_stats

def render_dashboard() -> None:

    stats = get_stats()

    st.markdown("## 📊 Dashboard")

    col1, col2 = st.columns(2)

    with col1:

        st.metric("📄 Documents", stats["documents"])
        st.metric("🧠 Embedding", stats["embedding_model"])

    with col2:
        st.metric("🧩 Chunks", stats["chunks"])
        st.metric("🗄️ Vector DB", stats["vector_db"])

    st.divider()