import logging
import streamlit as st

from backend_client import (
    get_documents,
    delete_document,
    download_document,
)

logger = logging.getLogger(__name__)


def render_knowledge_base():

    st.markdown("📚 Documents")

    st.caption(
        "Search, manage and delete documents in your knowledge base."
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

        filename = document["filename"]
        status = document.get("status", "completed")

        with st.container(border=True):

            col1, col2 = st.columns([9, 1])

            with col1:

                selectable = status == "completed"

                checked = st.checkbox(
                    f"📄 {filename}",
                    value=selectable,
                    disabled=not selectable,
                    key=f"select_{filename}",
                )

                col_a, col_b = st.columns(2)

                with col_a:

                    st.caption(
                        f"🧩 Chunks: {document.get('chunks', 0)}"
                    )

                with col_b:

                    if status == "completed":
                        st.caption("✅ Indexed")

                    elif status == "processing":
                        st.caption("⏳ Processing")

                    elif status == "failed":
                        st.caption("❌ Failed")

                    else:
                        st.caption(f"ℹ️ {status.title()}")

                if checked and selectable:
                    selected_documents.append(filename)

            with col2:

                with st.popover("⚙"):

                    if st.button(
                        "👁 View Details",
                        key=f"details_{filename}",
                        use_container_width=True,
                    ):

                        st.session_state.selected_document = document

                        st.rerun()

                    response = download_document(filename)

                    if response.status_code == 200:

                        st.download_button(
                            "⬇ Download",
                            data=response.content,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_{filename}",
                        )

                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{filename}",
                        use_container_width=True,
                    ):

                        st.session_state.confirm_delete = filename

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
                        f"**Filename:** {filename}"
                    )

                    st.write(
                        f"**Status:** {status.title()}"
                    )

                    st.write(
                        f"**Chunks:** {document.get('chunks', 0)}"
                    )

            if (
                st.session_state.get("confirm_delete")
                == filename
            ):

                st.warning(
                    f"Delete **{filename}**?"
                )

                yes_col, cancel_col = st.columns(2)

                with yes_col:

                    if st.button(
                        "Yes",
                        key=f"yes_{filename}",
                    ):

                        with st.spinner(
                            "Deleting document..."
                        ):

                            response = delete_document(filename)

                        if response.status_code == 200:

                            st.session_state.confirm_delete = None

                            st.success(
                                "✅ Document deleted successfully."
                            )

                            st.rerun()

                        else:

                            try:
                                detail = response.json().get(
                                    "detail",
                                    "Failed to delete document.",
                                )
                            except ValueError:
                                detail = (
                                    "Failed to delete document."
                                )

                            st.error(detail)

                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_{filename}",
                    ):

                        st.session_state.confirm_delete = None

                        st.rerun()

    logger.info(
        "Selected documents from knowledge base: %s",
        selected_documents,
    )

    return selected_documents