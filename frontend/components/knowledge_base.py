import streamlit as st

from backend_client import (
    get_documents,
    delete_document,
    download_document,
)


def render_knowledge_base():

    st.markdown("## 📚 Documents")
    st.caption(
        "Search, manage and delete indexed documents."
    )

    documents = get_documents()

    search_query = st.text_input(
        "🔍 Search Documents",
        placeholder="Type a filename...",
    )

    filtered_documents = [
        document
        for document in documents
        if search_query.lower() in document["filename"].lower()
    ]

    selected_documents = []

    if not documents:
        st.info(
            """
📂 No documents uploaded yet.

Upload your first PDF above to start building your knowledge base.
"""
        )
        return selected_documents

    if not filtered_documents:
        st.warning("No documents match your search.")
        return selected_documents

    for document in filtered_documents:

        with st.container(border=True):

            col1, col2 = st.columns([9, 1])

            with col1:

                checked = st.checkbox(
                    f"📄 {document['filename']}",
                    value=True,
                    key=f"select_{document['filename']}",
                )

                col_a, col_b = st.columns(2)

                with col_a:
                    st.caption(f"🧩 Chunks: {document['chunks']}")

                with col_b: 
                    st.caption("✅ Indexed")

                if checked:
                    selected_documents.append(
                        document["filename"]
                    )

            with col2:

                with st.popover("⚙"):

                    if st.button(
                        "👁 View Details",
                        key=f"details_{document['filename']}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_document = document

                        st.rerun()

                    response = download_document(document["filename"])
                    
                    if response.status_code == 200:

                        st.download_button(
                            "⬇ Download",
                            data=response.content,
                            file_name=document["filename"],
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_{document['filename']}",
                        )

                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{document['filename']}",
                        use_container_width=True,
                    ):

                        st.session_state.confirm_delete = (
                            document["filename"]
                        )

                        st.rerun()

            if (
                st.session_state.get("selected_document")
                == document
            ):

                with st.expander(
                    "📄 Document Details",
                    expanded=True,
                ):

                    st.write(
                        f"**Filename:** {document['filename']}"
                    )

                    st.write(
                        f"**Chunks:** {document['chunks']}"
                    )

            if (
                st.session_state.get("confirm_delete")
                == document["filename"]
            ):

                st.warning(
                    f"Delete **{document['filename']}**?"
                )

                yes_col, cancel_col = st.columns(2)

                with yes_col:

                    if st.button(
                        "Yes",
                        key=f"yes_{document['filename']}",
                    ):

                        with st.spinner(
                            "Deleting document..."
                        ):

                            response = delete_document(
                                document["filename"]
                            )

                        if response.status_code == 200:

                            st.session_state.confirm_delete = None

                            st.success(
                                "✅ Document deleted successfully."
                            )

                            st.rerun()

                        else:

                            detail = response.json().get(
                                "detail",
                                "Failed to delete document.",
                            )

                            st.error(detail)

                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_{document['filename']}",
                    ):

                        st.session_state.confirm_delete = None

                        st.rerun()