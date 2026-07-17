import streamlit as st

from state.session import (
    initialize_session,
    create_chat,
    switch_chat,
    delete_chat,
)


def render_chat_sidebar():

    initialize_session()

    st.markdown("## 💬 Chats")

    st.caption(
        "Start a new conversation or continue an existing one."
    )

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):
        create_chat()
        st.rerun()

    st.divider()

    for chat_id, chat in st.session_state.chats.items():

        col1, col2 = st.columns([5, 1])

        with col1:

            title = chat["title"]

            if chat_id == st.session_state.current_chat:
                title = "🟢 " + title

            if st.button(
                title,
                key=f"chat_{chat_id}",
                use_container_width=True,
            ):
                switch_chat(chat_id)
                st.rerun()

        with col2:

            if st.button(
                "🗑",
                key=f"delete_chat_{chat_id}",
            ):
                delete_chat(chat_id)
                st.rerun()

    st.divider()