import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from backend_client import ask_question, upload_pdf

from components.sidebar import render_sidebar
from components.chat import render_chat
from state.session import get_current_chat

from storage.chat_storage import (
    save_chat_file,
)


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

    if current_chat["title"] == "New Chat":
    
        current_chat["title"] = (
            question[:30] + "..."
            if len(question) > 30
            else question
        )
    save_chat_file(current_chat)
    
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

    save_chat_file(current_chat)

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