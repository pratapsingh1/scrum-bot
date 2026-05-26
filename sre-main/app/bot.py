
import os
import google.generativeai as genai

from dotenv import load_dotenv

from app.memory import get_user_history
from app.memory import save_user_message
from app.prompts import SCRUM_MASTER_PROMPT

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

BLOCKER_KEYWORDS = [
    "blocked",
    "issue",
    "stuck",
    "error",
    "failing",
    "deployment",
    "problem"
]


def detect_blocker(message):

    lower_message = message.lower()

    for keyword in BLOCKER_KEYWORDS:
        if keyword in lower_message:
            return True

    return False


def generate_followup_question(user_id, user_message):

    history = get_user_history(user_id)

    history_text = "\n".join(history[-5:])

    blocker_detected = detect_blocker(user_message)

    prompt = SCRUM_MASTER_PROMPT.format(
        history=history_text,
        user_message=user_message,
        blocker_detected=blocker_detected
    )

    response = model.generate_content(prompt)

    reply = response.text.strip()

    save_user_message(user_id, f"Developer: {user_message}")
    save_user_message(user_id, f"Bot: {reply}")

    return reply
