from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json

CHAT_DIR = Path("data/chats")

def init_storage():
    """
    Create the chat storage directory if it doesn't exist.
    """
    CHAT_DIR.mkdir(parents=True, exist_ok=True)

def create_chat_file():

    init_storage()

    now = datetime.now().isoformat()

    chat = {
        "id": str(uuid4()),
        "title": "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }

    chat_path = CHAT_DIR / f"{chat['id']}.json"

    with open(chat_path, "w", encoding="utf-8") as file:
        json.dump(chat, file, indent=4)

    return chat

def save_chat_file(chat):

    chat["updated_at"] = datetime.now().isoformat()

    chat_path = CHAT_DIR / f"{chat['id']}.json"

    with open(chat_path, "w", encoding="utf-8") as file:
        json.dump(chat, file, indent=4)

def load_chat_file(chat_id):

    chat_path = CHAT_DIR / f"{chat_id}.json"

    if not chat_path.exists():
        return None

    with open(chat_path, "r", encoding="utf-8") as file:
        chat = json.load(file)

    return chat

def list_chat_files():

    init_storage()

    chats = []

    for chat_file in CHAT_DIR.glob("*.json"):

        with open(chat_file, "r", encoding="utf-8") as file:
            chat = json.load(file)

        chats.append(
            {
                "id": chat["id"],
                "title": chat["title"],
                "updated_at": chat["updated_at"],
                "pinned": chat.get("pinned", False),
            }
        )

    chats.sort(
        key=lambda chat: datetime.fromisoformat(chat["updated_at"]),
        reverse=True,
    )

    pinned = [chat for chat in chats if chat.get("pinned", False)]
    others = [chat for chat in chats if not chat.get("pinned", False)]

    return pinned + others

def delete_chat_file(chat_id):

    chat_path = CHAT_DIR / f"{chat_id}.json"

    if chat_path.exists():
        chat_path.unlink()

def update_chat_title(chat_id, title):

    chat = load_chat_file(chat_id)

    if chat is None:
        return

    chat["title"] = title
    save_chat_file(chat)

def rename_chat(chat_id, new_title):

    chat = load_chat_file(chat_id)

    if chat is None:
        return

    new_title = new_title.strip()

    if not new_title:
        return

    chat["title"] = new_title

    save_chat_file(chat)

def pin_chat(chat_id):

    chat = load_chat_file(chat_id)

    if chat is None:
        return

    chat["pinned"] = not chat.get("pinned", False)

    save_chat_file(chat)