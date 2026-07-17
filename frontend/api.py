import requests
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    documents: list[str] = []


BASE_URL = "http://127.0.0.1:8000"


def upload_pdf(file):
    print(file.name)
    print(file.type)

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

    print(response.status_code)
    print(response.text)

    response.raise_for_status()

    return response.json()


def ask_question(
    question: str,
    documents: list[str] | None = None,
) -> dict:

    print("Asking:", f"{BASE_URL}/chat")
    print("Question:", question)
    print("Documents sent:", documents)

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "question": question,
            "documents": documents,
        },
        timeout=60,
    )

    print(response.status_code)
    print(response.text)

    response.raise_for_status()

    return response.json()

def get_documents():

    response = requests.get(
        f"{BASE_URL}/documents",
        timeout = 30,
    )

    response.raise_for_status()

    return response.json()


def get_stats():

    response = requests.get(
        f"{BASE_URL}/stats",
        timeout = 30,
    )

    response.raise_for_status()
    
    return response.json()

def delete_document(filename):

    response = requests.delete(
        f"{BASE_URL}/documents/{filename}"
    )

    return response.json()