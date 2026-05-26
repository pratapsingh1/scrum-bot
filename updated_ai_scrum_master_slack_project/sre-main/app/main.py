
import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from slack_sdk import WebClient

from app.bot import generate_followup_question
from app.slack_blocks import create_standup_block
from app.memory import save_user_message

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "AI Scrum Master Bot Running"
    }


@app.post("/slack/events")
async def slack_events(request: Request):

    data = await request.json()

    if "challenge" in data:
        return JSONResponse({"challenge": data["challenge"]})

    event = data.get("event", {})

    if event.get("type") == "message" and "bot_id" not in event:

        user_id = event.get("user")
        text = event.get("text")
        channel_id = event.get("channel")

        if text.lower() == "start standup":

            blocks = create_standup_block(
                user_name="Developer",
                tasks=[
                    "UI Automation",
                    "Notification Testing",
                    "Slack Integration"
                ]
            )

            client.chat_postMessage(
                channel=channel_id,
                text="Daily Standup",
                blocks=blocks
            )

            return JSONResponse({"status": "sent"})

        reply = generate_followup_question(
            user_id=user_id,
            user_message=text
        )

        save_user_message(user_id, text)

        client.chat_postMessage(
            channel=channel_id,
            text=reply
        )

    return JSONResponse({"status": "ok"})


@app.post("/slack/interactions")
async def slack_interactions(request: Request):

    form_data = await request.form()

    payload = json.loads(form_data["payload"])

    user_id = payload["user"]["id"]
    channel_id = payload["channel"]["id"]

    action = payload["actions"][0]["action_id"]

    if action == "on_track_btn":

        reply = (
            "Great! What is your primary focus "
            "for today?"
        )

    elif action == "blocked_btn":

        reply = (
            "Understood. What blocker "
            "is impacting your progress?"
        )

    else:
        reply = "Thanks for the update."

    client.chat_postMessage(
        channel=channel_id,
        text=reply
    )

    return JSONResponse({"status": "ok"})
