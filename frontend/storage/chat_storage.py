from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json


CHAT_DIR = Path("data/chats")


def get_user_chat_dir(user_id: int) -> Path:
    """
    Return the chat directory belonging to a specific user.
    """
    return CHAT_DIR / str(user_id)


def init_storage(user_id: int):
    """
    Create the authenticated user's chat storage directory.
    """
    user_chat_dir = get_user_chat_dir(user_id)
    user_chat_dir.mkdir(parents=True, exist_ok=True)


def create_chat_file(user_id: int):

    init_storage(user_id)

    now = datetime.now().isoformat()

    chat = {
        "id": str(uuid4()),
        "user_id": user_id,
        "title": "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }

    chat_path = (
        get_user_chat_dir(user_id)
        / f"{chat['id']}.json"
    )

    with open(chat_path, "w", encoding="utf-8") as file:
        json.dump(chat, file, indent=4)

    return chat


def save_chat_file(chat, user_id: int):

    init_storage(user_id)

    # Prevent saving a chat belonging to another user.
    if chat.get("user_id") != user_id:
        raise PermissionError("Chat does not belong to this user.")

    chat["updated_at"] = datetime.now().isoformat()

    chat_path = (
        get_user_chat_dir(user_id)
        / f"{chat['id']}.json"
    )

    with open(chat_path, "w", encoding="utf-8") as file:
        json.dump(chat, file, indent=4)


def load_chat_file(chat_id, user_id: int):

    chat_path = (
        get_user_chat_dir(user_id)
        / f"{chat_id}.json"
    )

    if not chat_path.exists():
        return None

    with open(chat_path, "r", encoding="utf-8") as file:
        chat = json.load(file)

    # Defense-in-depth ownership check.
    if chat.get("user_id") != user_id:
        return None

    return chat


def list_chat_files(user_id: int):

    init_storage(user_id)

    chats = []

    user_chat_dir = get_user_chat_dir(user_id)

    for chat_file in user_chat_dir.glob("*.json"):

        with open(chat_file, "r", encoding="utf-8") as file:
            chat = json.load(file)

        # Ignore files that don't belong to this user.
        if chat.get("user_id") != user_id:
            continue

        chats.append(
            {
                "id": chat["id"],
                "title": chat["title"],
                "updated_at": chat["updated_at"],
                "pinned": chat.get("pinned", False),
            }
        )

    chats.sort(
        key=lambda chat: datetime.fromisoformat(
            chat["updated_at"]
        ),
        reverse=True,
    )

    pinned = [
        chat
        for chat in chats
        if chat.get("pinned", False)
    ]

    others = [
        chat
        for chat in chats
        if not chat.get("pinned", False)
    ]

    return pinned + others


def delete_chat_file(chat_id, user_id: int):

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        return

    chat_path = (
        get_user_chat_dir(user_id)
        / f"{chat_id}.json"
    )

    if chat_path.exists():
        chat_path.unlink()


def update_chat_title(
    chat_id,
    title,
    user_id: int,
):

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        return

    chat["title"] = title

    save_chat_file(
        chat,
        user_id,
    )


def rename_chat(
    chat_id,
    new_title,
    user_id: int,
):

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        return

    new_title = new_title.strip()

    if not new_title:
        return

    chat["title"] = new_title

    save_chat_file(
        chat,
        user_id,
    )


def pin_chat(
    chat_id,
    user_id: int,
):

    chat = load_chat_file(
        chat_id,
        user_id,
    )

    if chat is None:
        return

    chat["pinned"] = not chat.get(
        "pinned",
        False,
    )

    save_chat_file(
        chat,
        user_id,
    )