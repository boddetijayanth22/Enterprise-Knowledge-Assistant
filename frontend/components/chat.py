import streamlit as st

from state.session import get_current_chat

def render_chat():

    current_chat = get_current_chat()

    st.title("Enterprise Knowledge Assistant")

    st.caption(
        "Semantic Search powered by Gemini + Qdrant"
    )

    st.divider()

    for message in current_chat["messages"]:

        with st.chat_message(message["role"]):

            if message["role"] == "assistant":

                st.markdown(message["content"])

            else:

                st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and "sources" in message
            ):

                with st.expander("Sources"):

                    for source in message["sources"]:

                        st.markdown(
                            f"""
                        📄 **{source['file']}**

                        📖 Page **{source['page']}**
                        """
                        )

                        st.divider()

    question = st.chat_input(
        "Ask anything about your documents..."
    )

    return question