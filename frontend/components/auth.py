import streamlit as st

from frontend.auth import is_authenticated, login, logout


def render_auth():

    if is_authenticated():
        st.sidebar.success("Authenticated")

        if st.sidebar.button("Logout"):
            logout()
            st.rerun()

        return True

    st.title("Enterprise Knowledge Assistant")

    st.subheader("Login")

    username = st.text_input(
        "Username",
        key="login_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
    )

    if st.button("Login", type="primary"):

        if not username or not password:
            st.error("Please enter username and password.")
            return False

        success, message = login(
            username,
            password,
        )

        if success:
            st.success(message)
            st.rerun()

        st.error(message)

    return False