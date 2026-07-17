import streamlit as st

from api import (
    get_documents,
    delete_document,
)


def render_knowledge_base():

    st.markdown(" ## 📚 Documents")

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
        if search_query.lower()
        in document["filename"].lower()
    ]

    selected_documents = []

    if not filtered_documents:
        st.info(
            """
    📂 No documents uploaded yet.

    Upload your first PDF above to start building your knowledge base.
    """
        )

    elif not filtered_documents:

        st.warning(
            "No documents match your search."
        )

    for document in filtered_documents:

        container = st.container(border=True)

        with container:

            col1, col2 = st.columns([8, 1])

            with col1:

                checked = st.checkbox(
                    document["filename"],
                    value=True,
                    key=f"select_{document['filename']}",
                )

                st.caption(
                    f"🧩 Chunks: {document['chunks']}"
                )

                if checked:
                    selected_documents.append(
                        document["filename"]
                )            

            with col2:
            
                st.write("")

            if st.button(
                "🗑",
                key=f"delete_{document['filename']}",
            ):

                with st.spinner("Deleting document..."):

                    delete_document(
                        document["filename"]
                    )

                st.success("Document deleted.")

                st.rerun()

    st.divider()

    return selected_documents