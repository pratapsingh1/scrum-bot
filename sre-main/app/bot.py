import os
import json
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


# ---------------------------------------------------
# BLOCKER DETECTION
# ---------------------------------------------------

def detect_blocker(message):

    lower_message = message.lower()

    for keyword in BLOCKER_KEYWORDS:

        if keyword in lower_message:
            return True

    return False


# ---------------------------------------------------
# SCRUM FOLLOWUP AI
# ---------------------------------------------------

def generate_followup_question(user_id, user_message):

    history = get_user_history(user_id)

    developer_messages = [
        msg for msg in history
        if msg.startswith("Developer:")
    ]

    question_count = len(developer_messages)

    save_user_message(
        user_id,
        f"Developer: {user_message}"
    )

    # Question 1 completed
    if question_count == 0:
        reply = (
            "Thanks. Do you have any blockers "
            "or challenges currently?"
        )

    # Question 2 completed
    elif question_count == 1:

        if detect_blocker(user_message):

            reply = (
                "Understood. Please share the blocker "
                "and I'll note it in today's standup."
            )

        else:

            reply = (
                "Great. Is there any support needed "
                "from the team today?"
            )

    # Question 3 completed
    else:

        reply = (
            "✅ Thanks for the update.\n\n"
            "Your standup has been recorded.\n\n"
            "Have a productive day!"
        )

    save_user_message(
        user_id,
        f"Bot: {reply}"
    )

    return reply



# ---------------------------------------------------
# JIRA SPRINT STRUCTURE GENERATOR
# ---------------------------------------------------

def generate_jira_structure(user_prompt):

    prompt = f'''
You are an expert Agile Scrum Master.

Convert the following requirement into:

1. Epic
2. User Stories
3. Tasks

Return STRICT JSON format only.

Format:

{{
  "epic": {{
    "title": "",
    "description": ""
  }},
  "stories": [
    {{
      "title": "",
      "description": "",
      "tasks": [
        ""
      ]
    }}
  ]
}}

Requirement:
{user_prompt}
'''

    response = model.generate_content(prompt)

    text = response.text.strip()

    # REMOVE markdown formatting
    text = text.replace("```json", "")
    text = text.replace("```", "")

    try:

        parsed = json.loads(text)

        return parsed

    except Exception as e:

        return {
            "error": str(e),
            "raw_response": text
        }


# ---------------------------------------------------
# MODIFY EXISTING SPRINT
# ---------------------------------------------------

def modify_sprint(original_prompt, modification_prompt):

    prompt = f'''
You are an Agile Scrum AI Assistant.

Original Sprint Requirement:
{original_prompt}

Modification Request:
{modification_prompt}

Update the sprint structure accordingly.

Return proper readable response.
'''

    response = model.generate_content(prompt)

    return response.text.strip()

