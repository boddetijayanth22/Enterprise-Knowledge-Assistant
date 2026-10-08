import streamlit as st

from frontend.auth import get_current_user_id

from frontend.storage.chat_storage import (
    create_chat_file,
    save_chat_file,
    load_chat_file,
    list_chat_files,
    delete_chat_file,
)


def initialize_session():

    user_id = get_current_user_id()

    if user_id is None:
        return

    if (
        "chat_initialized_user_id"
        not in st.session_state
        or st.session_state.chat_initialized_user_id
        != user_id
    ):

        st.session_state.pop(
            "current_chat",
            None,
        )

        st.session_state.chat_initialized_user_id = user_id

    if "selected_document" not in st.session_state:
        st.session_state.selected_document = None

    if "rename_chat" not in st.session_state:
        st.session_state.rename_chat = None

    if "current_chat" not in st.session_state:

        chats = list_chat_files(user_id)

        if chats:

            st.session_state.current_chat = chats[0]["id"]

        else:

            create_chat()


def create_chat():

    user_id = get_current_user_id()

    if user_id is None:
        return

    chat = create_chat_file(user_id)

    st.session_state.current_chat = chat["id"]


def get_current_chat():

    user_id = get_current_user_id()

    if user_id is None:
        return {
            "messages": [],
        }

    chat_id = st.session_state.get(
        "current_chat"
    )

    if not chat_id:
        create_chat()
        chat_id = st.session_state.current_chat

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        create_chat()

        chat = load_chat_file(
            st.session_state.current_chat,
            user_id,
        )

    return chat


def save_current_chat(chat):

    user_id = get_current_user_id()

    if user_id is None:
        return

    save_chat_file(
        chat,
        user_id,
    )


def switch_chat(chat_id):

    user_id = get_current_user_id()

    if user_id is None:
        return

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        return

    st.session_state.current_chat = chat_id


def delete_chat(chat_id):

    user_id = get_current_user_id()

    if user_id is None:
        return

    chats = list_chat_files(user_id)

    if len(chats) == 1:
        return

    delete_chat_file(
        chat_id,
        user_id,
    )

    chats = list_chat_files(user_id)

    if chats:
        st.session_state.current_chat = chats[0]["id"]

    else:
        create_chat()