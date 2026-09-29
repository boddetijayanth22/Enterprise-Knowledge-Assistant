import streamlit as st

from frontend.auth import get_current_user_id

from frontend.state.session import (
    initialize_session,
    create_chat,
    switch_chat,
    delete_chat,
)

from frontend.storage.chat_storage import (
    list_chat_files,
    rename_chat,
    pin_chat,
)


@st.dialog("Rename Chat")
def rename_chat_dialog(
    chat_id,
    current_title,
):

    new_title = st.text_input(
        "Chat Title",
        value=current_title,
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Save",
            use_container_width=True,
        ):

            user_id = get_current_user_id()

            rename_chat(
                chat_id,
                new_title,
                user_id,
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.rerun()


def render_chat_item(chat):

    chat_id = chat["id"]

    title = chat["title"]

    col_pin, col_title, col_menu = st.columns(
        [0.6, 7.4, 1]
    )

    with col_pin:

        if chat.get("pinned", False):
            st.markdown("  📌")

    with col_title:

        button_type = "secondary"

        if (
            chat_id
            == st.session_state.current_chat
        ):
            button_type = "primary"

        if st.button(
            title,
            key=f"chat_{chat_id}",
            use_container_width=True,
            type=button_type,
        ):

            st.session_state.rename_chat = None

            switch_chat(chat_id)

            st.rerun()

    with col_menu:

        with st.popover("☰"):

            if st.button(
                "✏️ Rename",
                key=f"rename_{chat_id}",
                use_container_width=True,
            ):

                rename_chat_dialog(
                    chat_id,
                    chat["title"],
                )

                st.session_state.rename_chat = chat_id

            pin_label = (
                "📍 Unpin Chat"
                if chat.get("pinned", False)
                else "📌 Pin Chat"
            )

            if st.button(
                pin_label,
                key=f"pin_{chat_id}",
                use_container_width=True,
            ):

                user_id = get_current_user_id()

                pin_chat(
                    chat_id,
                    user_id,
                )

                st.rerun()

            if st.button(
                "🗑 Delete",
                key=f"delete_chat_{chat_id}",
                use_container_width=True,
            ):

                delete_chat(chat_id)

                st.rerun()


def render_chat_sidebar():

    initialize_session()

    user_id = get_current_user_id()

    if user_id is None:
        return

    st.markdown("## 💬 Chats")

    st.caption(
        "Start a new conversation or continue an existing one."
    )

    search_query = st.text_input(
        "🔍 Search Chats",
        placeholder="Type a chat title...",
    )

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        st.session_state.rename_chat = None

        create_chat()

        st.rerun()

    st.divider()

    chats = list_chat_files(user_id)

    filtered_chats = [
        chat
        for chat in chats
        if search_query.lower()
        in chat["title"].lower()
    ]

    if not filtered_chats:

        st.caption("No chats found.")

        return

    pinned_chats = [
        chat
        for chat in filtered_chats
        if chat.get("pinned", False)
    ]

    other_chats = [
        chat
        for chat in filtered_chats
        if not chat.get("pinned", False)
    ]

    if pinned_chats:

        st.caption("Pinned")

        for chat in pinned_chats:
            render_chat_item(chat)

    if other_chats:

        st.caption("")

        for chat in other_chats:
            render_chat_item(chat)