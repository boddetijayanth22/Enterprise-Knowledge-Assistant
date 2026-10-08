import streamlit as st


def render_upload_panel() -> tuple[list[object], bool]:

    st.markdown("## 📤 Upload Documents")

    st.caption(
        "Upload one or more PDF documents to your knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Choose PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        key="document_uploader",
        help=(
            "Select multiple PDFs at once using Ctrl/Shift, "
            "or click + to add more files."
        ),
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.info(
            f"📄 {len(uploaded_files)} PDF(s) currently selected"
        )

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1,
        ):
            st.write(
                f"{index}. `{uploaded_file.name}` "
                f"— {uploaded_file.size / (1024 * 1024):.2f} MB"
            )

    else:
        st.caption("No PDF selected.")

    upload = st.button(
        "📤 Upload",
        use_container_width=True,
    )

    st.divider()

    return uploaded_files, upload