import time
import logging
import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_client import (
    ask_question,
    upload_pdf,
    get_document_statuses,
)

from components.sidebar import render_sidebar
from components.chat import render_chat

from frontend.state.session import get_current_chat

from frontend.auth import get_current_user_id
from frontend.components.auth import render_auth

from frontend.storage.chat_storage import save_chat_file


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    layout="wide",
)

if not render_auth():
    st.stop()

uploaded_files, upload, selected_documents = render_sidebar()

if uploaded_files:
    logger.info(
        "Selected upload files: %s",
        [file.name for file in uploaded_files],
    )
    
question = render_chat()

if question:

    current_chat = get_current_chat()

    user_id = get_current_user_id()

    if user_id is None:
        st.error("Authenticated user not found.")
        st.stop()

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

    save_chat_file(
        current_chat,
        user_id,
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("🤖 Generating answer..."):

        logger.info(
            "Selected documents passed to ask_question: %s",
            selected_documents,
        )

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

    save_chat_file(
        current_chat,
        user_id,
    )

    st.rerun()

if upload:
    if not uploaded_files:
        st.warning("Upload at least one PDF first.")
    else:
        successful_uploads = []
        failed_uploads = []

        upload_status = st.status(
            "📤 Uploading documents...",
            expanded=True,
        )

        for uploaded_file in uploaded_files:
            upload_status.write(f"Uploading `{uploaded_file.name}`...")

            result = upload_pdf(uploaded_file)

            if result:
                successful_uploads.append(uploaded_file.name)
                upload_status.write(f"✅ `{uploaded_file.name}` accepted")
            else:
                failed_uploads.append(uploaded_file.name)
                upload_status.write(f"❌ `{uploaded_file.name}` failed")

        if failed_uploads:
            upload_status.update(
                label="⚠️ Upload completed with errors",
                state="error",
            )
        else:
            upload_status.update(
                label="✅ Uploads accepted — indexing started",
                state="complete",
            )

        if successful_uploads:
            indexing_status = st.status(
                "⏳ Indexing documents...",
                expanded=True,
            )

            pending_files = set(successful_uploads)
            timeout_seconds = 300
            start_time = time.time()

            while pending_files and time.time() - start_time < timeout_seconds:
                documents = get_document_statuses()

                status_map = {
                    document["filename"]: document["status"]
                    for document in documents
                }

                for filename in list(pending_files):
                    status = status_map.get(filename)

                    if status == "completed":
                        indexing_status.write(
                            f"✅ `{filename}` indexed successfully"
                        )
                        pending_files.remove(filename)

                    elif status == "failed":
                        indexing_status.write(
                            f"❌ `{filename}` indexing failed"
                        )
                        pending_files.remove(filename)

                if pending_files:
                    time.sleep(2)

            if pending_files:
                indexing_status.update(
                    label="⚠️ Indexing timed out",
                    state="error",
                )
                for filename in pending_files:
                    indexing_status.write(
                        f"⏱️ `{filename}` did not finish within 5 minutes"
                    )
            else:
                indexing_status.update(
                    label="✅ All documents indexed",
                    state="complete",
                )

        st.rerun()