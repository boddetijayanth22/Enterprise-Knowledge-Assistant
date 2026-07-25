import streamlit as st

from storage.chat_storage import (
    create_chat_file,
    save_chat_file,
    load_chat_file,
    list_chat_files,
    delete_chat_file,
)


def initialize_session():

    if "selected_document" not in st.session_state:
        st.session_state.selected_document = None

    if "rename_chat" not in st.session_state:
        st.session_state.rename_chat = None

    if "current_chat" not in st.session_state:

        chats = list_chat_files()

        if chats:

            st.session_state.current_chat = chats[0]["id"]

        else:

            create_chat()

def create_chat():

    chat = create_chat_file()

    st.session_state.current_chat = chat["id"]

def get_current_chat():

    return load_chat_file(
        st.session_state.current_chat
    )

def switch_chat(chat_id):

    st.session_state.current_chat = chat_id

def delete_chat(chat_id):

    chats = list_chat_files()

    if len(chats) == 1:
        return

    delete_chat_file(chat_id)

    chats = list_chat_files()

    st.session_state.current_chat = chats[0]["id"]