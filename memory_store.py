import json
import re
import hashlib
from pathlib import Path

MEMORY_FILE = Path("farmer_memory.json")
HISTORY_DIR = Path("farmer_chat_histories")


def normalize_user_id(email):
    """Use a normalized email as the farmer's identity."""
    return email.strip().lower()


def safe_file_id(user_id):
    """Create a safe, stable file identifier."""
    return hashlib.sha256(
        normalize_user_id(user_id).encode("utf-8")
    ).hexdigest()


def load_memory():
    if MEMORY_FILE.exists():
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_farmer_data(user_id, crop, problem):
    user_id = normalize_user_id(user_id)
    farmer_memory = load_memory()

    farmer_memory[user_id] = {
        "previous_crop": crop,
        "previous_problem": problem,
    }

    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(farmer_memory, file, indent=4, ensure_ascii=False)


def get_farmer_data(user_id):
    user_id = normalize_user_id(user_id)
    return load_memory().get(user_id, {})


def history_path(user_id):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_DIR / f"{safe_file_id(user_id)}.json"


def get_chat_history(user_id):
    path = history_path(user_id)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_chat_history(user_id, role, message):
    history = get_chat_history(user_id)

    history.append({
        "role": role,
        "message": message,
    })

    path = history_path(user_id)

    with path.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)