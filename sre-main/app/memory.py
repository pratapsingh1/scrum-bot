
import json
import os

MEMORY_FILE = "app/conversation_memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as file:
        try:
            return json.load(file)
        except:
            return {}


def save_memory(data):

    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_user_history(user_id):

    memory = load_memory()

    return memory.get(user_id, [])


def save_user_message(user_id, message):

    memory = load_memory()

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append(message)

    save_memory(memory)
