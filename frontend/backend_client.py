import requests
import streamlit as st
from app.utils.logger import logger
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    documents: list[str] = []
    mode: str


BASE_URL = "http://127.0.0.1:8000"


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
    )

    logger.info(response.status_code)
    logger.info(response.text)

    try:
        response.raise_for_status()
    except requests.HTTPError:
        st.error("Backend request failed.")
        raise

    return response.json()


def ask_question(
    question: str,
    documents: list[str] | None = None,
) -> dict:

    logger.info(f"Asking: {BASE_URL}/chat")
    logger.info(f"Question: {question}")
    logger.info(f"Documents sent {documents}")
    

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "question": question,
            "documents": documents or [],
            "mode": st.session_state.search_mode,
        },
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
        timeout = 30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        st.error("Backend request failed.")
        raise

    return response.json()


def get_stats():

    response = requests.get(
        f"{BASE_URL}/stats",
        timeout = 30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        st.error("Backend request failed.")
        raise
    
    return response.json()

def delete_document(filename):

    return requests.delete(
        f"{BASE_URL}/documents/{filename}"
    )

def download_document(filename):

    return requests.get(
        f"{BASE_URL}/documents/{filename}/download",
        stream=True,
    )