import os
import json

MEMORY_DIR = "memory"

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)


# ---------------------------------------------------
# GET USER FILE
# ---------------------------------------------------

def get_user_file(user_id):

    return os.path.join(
        MEMORY_DIR,
        f"{user_id}.json"
    )


# ---------------------------------------------------
# LOAD MEMORY
# ---------------------------------------------------

def load_memory(user_id):

    file_path = get_user_file(user_id)

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:

        return json.load(f)


# ---------------------------------------------------
# SAVE MEMORY
# ---------------------------------------------------

def save_memory(user_id, memory):

    file_path = get_user_file(user_id)

    with open(file_path, "w") as f:

        json.dump(memory, f, indent=2)


# ---------------------------------------------------
# SAVE USER MESSAGE
# ---------------------------------------------------

def save_user_message(user_id, message):

    memory = load_memory(user_id)

    memory.append(message)

    save_memory(user_id, memory)


# ---------------------------------------------------
# GET USER HISTORY
# ---------------------------------------------------

def get_user_history(user_id):

    return load_memory(user_id)

