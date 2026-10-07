import os
import requests
import streamlit as st


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


def _reset_user_session_state():
    """
    Clear user-specific Streamlit state when switching users.
    """

    keys_to_clear = [
        "current_chat",
        "selected_document",
        "rename_chat",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


def login(username: str, password: str):
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "username": username,
            "password": password,
        },
        timeout=30,
    )

    if response.status_code != 200:
        return False, "Invalid username or password."

    data = response.json()

    access_token = data["access_token"]

    st.session_state.access_token = access_token

    me_response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        timeout=30,
    )

    if me_response.status_code != 200:
        _reset_user_session_state()

        st.session_state.access_token = None
        st.session_state.authenticated = False

        return False, "Unable to retrieve authenticated user."

    user = me_response.json()

    _reset_user_session_state()

    st.session_state.user_id = user["id"]
    st.session_state.username = user["username"]
    st.session_state.user_role = user["role"]

    st.session_state.authenticated = True

    return True, "Login successful."


def logout():
    """
    Clear authentication and user-specific Streamlit state.
    """

    _reset_user_session_state()

    st.session_state.access_token = None
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None


def get_auth_headers():
    token = st.session_state.get("access_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
    }


def get_current_user_id():
    return st.session_state.get("user_id")


def is_authenticated():
    return bool(
        st.session_state.get("authenticated", False)
        and st.session_state.get("access_token")
        and st.session_state.get("user_id")
    )