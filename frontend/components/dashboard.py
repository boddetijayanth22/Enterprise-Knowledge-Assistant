import streamlit as st

from backend_client import get_stats

def render_dashboard() -> None:

    stats = get_stats()

    st.markdown("## 📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📄 Documents",
            stats["documents"],
        )

    with col2:
        st.metric(
            "🧩 Chunks",
            stats["chunks"],
        )

    with col3:
        st.metric(
            "🧠 Embedding",
            stats["embedding_model"],
        )

    with col4:
        st.metric(
            "🗄️ Vector DB",
            stats["vector_db"],
        )

    st.subheader("⚙ System Information")
        
    left, right = st.columns(2)

    with left:

        st.info(
            f"""
**Embedding Model**

{stats["embedding_model"]}
"""
        )

    with right:

        st.success(
            f"""
**Vector Database**

{stats["vector_db"]}
"""
    )

    mode = st.session_state.get(
        "selected_mode",
         "Semantic"
    )
    st.write(
        f"Current Search Mode: **{mode}**"
    )