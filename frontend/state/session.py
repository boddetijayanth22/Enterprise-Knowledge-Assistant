import streamlit as st
import uuid


def initialize_session():
    """
    Initialize the application state.
    """

    if "chats" not in st.session_state:

        chat_id = str(uuid.uuid4())

        st.session_state.chats = {
            chat_id: {
                "title": "New Chat",
                "messages": [],
            }
        }

        st.session_state.current_chat = chat_id


def create_chat():
    """
    Create a new chat session.
    """

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
    }

    st.session_state.current_chat = chat_id


def get_current_chat():

    return st.session_state.chats[
        st.session_state.current_chat
    ]


def switch_chat(chat_id):

    st.session_state.current_chat = chat_id

def delete_chat(chat_id):

    if len(st.session_state.chats) == 1:
        return

    del st.session_state.chats[chat_id]

    st.session_state.current_chat = next(
        iter(st.session_state.chats)
    )