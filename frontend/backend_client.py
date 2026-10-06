import logging
import os

import requests
import streamlit as st

from frontend.auth import get_auth_headers

logger = logging.getLogger(__name__)


BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


def upload_pdf(file):
    logger.info(file.name)
    logger.info(file.type)

    response = requests.post(
        f"{BASE_URL}/upload",
        files={
            "file": (
                file.name,
                file.getvalue(),
                "application/pdf",
            )
        },
        headers=get_auth_headers(),
        timeout=60,
    )

    logger.info(response.status_code)
    logger.info(response.text)

    if response.status_code == 409:
        try:
            detail = response.json().get(
                "detail",
                "Document already exists.",
            )
        except ValueError:
            detail = "Document already exists."

        st.warning(f"⚠️ {detail}")
        return None

    try:
        response.raise_for_status()
    except requests.HTTPError:
        try:
            detail = response.json().get(
                "detail",
                response.text,
            )
        except ValueError:
            detail = response.text

        st.error(f"❌ Upload failed: {detail}")
        return None

    return response.json()


def ask_question(
    question: str,
    documents: list[str] | None = None,
) -> dict:

    logger.info(f"Asking: {BASE_URL}/chat")
    logger.info(f"Question: {question}")
    logger.info(f"Documents sent: {documents}")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "question": question,
            "documents": documents,
            "mode": st.session_state.search_mode,
        },
        headers=get_auth_headers(),
        timeout=60,
    )

    logger.info(response.status_code)
    logger.info(response.text)

    try:
        response.raise_for_status()
    except requests.HTTPError:
        st.error("Backend request failed.")
        raise

    return response.json()


def get_documents():

    response = requests.get(
        f"{BASE_URL}/documents",
        headers=get_auth_headers(),
        timeout=30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        st.error("Backend request failed.")
        raise

    return response.json()["documents"]


def get_stats():

    response = requests.get(
        f"{BASE_URL}/stats",
        headers=get_auth_headers(),
        timeout=30,
    )

    if response.status_code == 429:
        st.warning(
            "⚠️ Dashboard is temporarily rate limited. "
            "Please try again shortly."
        )
        return None

    try:
        response.raise_for_status()
    except requests.HTTPError:
        try:
            detail = response.json().get(
                "detail",
                response.text,
            )
        except ValueError:
            detail = response.text

        st.error(
            f"❌ Unable to load dashboard statistics: "
            f"{detail}"
        )
        return None

    data = response.json()

    return {
        "documents": data["total_documents"],
        "chunks": data["total_chunks"],
        "embedding_model": data["embedding_model"],
    }


def delete_document(filename):

    response = requests.delete(
        f"{BASE_URL}/documents/{filename}",
        headers=get_auth_headers(),
        timeout=30,
    )

    return response


def download_document(filename):

    return requests.get(
        f"{BASE_URL}/documents/{filename}/download",
        headers=get_auth_headers(),
        stream=True,
        timeout=30,
    )