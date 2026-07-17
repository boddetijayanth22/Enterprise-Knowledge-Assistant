import streamlit as st

from api import (
    ask_question,
    upload_pdf,
)

from components.sidebar import render_sidebar
from components.chat import render_chat
from state.session import get_current_chat


st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    layout="wide",
)

uploaded_file, upload, selected_documents = render_sidebar()

question = render_chat()

if question:

    current_chat = get_current_chat()

    current_chat["messages"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    if (
        current_chat["title"] == "New Chat"
    ):
    
        current_chat["title"] = (
            question[:30] + "..."
            if len(question) > 30
            else question
        )

    with st.spinner(
        "🔍 Retrieving relevant documents...\n\n🤖 Generating answer..."
    ):

        result = ask_question(
            question,
            selected_documents,
        )

    current_chat["messages"].append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )

    st.rerun()

if upload:

    if uploaded_file is None:

        st.warning("Upload a PDF first.")

    else:
        with st.spinner("📄 Uploading PDF..."):

            result = upload_pdf(uploaded_file)

        st.success(
            f"✅ {result['filename']} uploaded successfully!"
        )

        st.rerun()