import streamlit as st


def render_upload_panel() -> tuple[object, bool]:

    st.markdown("## 📤 Upload Documents")

    st.caption(
        "Upload one or more PDF documents to your knowledge base."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    upload = st.button(
        "📤 Upload",
        use_container_width=True,
    )

    st.divider()

    return uploaded_file, upload