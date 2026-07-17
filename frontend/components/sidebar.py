from components.chat_sidebar import render_chat_sidebar
from components.dashboard import render_dashboard
from components.search_mode import render_search_mode
from components.knowledge_base import render_knowledge_base
from components.upload_panel import render_upload_panel

import streamlit as st

def render_sidebar():

    st.markdown("# Enterprise Knowledge Assistant")

    st.caption(
        "Semantic Search powered by Gemini + Qdrant and FastAPI"
    )

    st.divider()

    render_chat_sidebar()

    uploaded_file, upload = render_upload_panel()

    selected_documents = render_knowledge_base()

    render_dashboard()

    render_search_mode()

    if st.button(
        "🔄 Refresh Knowledge Base",
        use_container_width=True,
    ):
        st.rerun()

    return (
        uploaded_file,
        upload,
        selected_documents,
    )