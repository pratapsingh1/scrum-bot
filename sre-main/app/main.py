```python
import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from slack_sdk import WebClient

from app.bot import (
    generate_followup_question,
    generate_jira_structure,
    modify_sprint
)

from app.slack_blocks import create_standup_block
from app.memory import save_user_message, load_memory, save_memory

from app.jira import (
    create_jira_issues_from_structure,
    jira_is_configured
)

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)


@app.get("/")
async def home():

    return RedirectResponse(
        url="https://app.slack.com/client/T0B5TU4DY49/D0B5S5NQ8G2",
        status_code=302
    )


# -----------------------------
# AI ASSISTANT UI
# -----------------------------

@app.get("/assistant", response_class=HTMLResponse)
async def assistant_ui(request: Request):

    return templates.TemplateResponse(
        "assistant.html",
        {"request": request}
    )


@app.post("/generate")
async def generate(prompt: str = Form(...)):

    structure = generate_jira_structure(prompt)

    jira_response = None

    if jira_is_configured():
        jira_response = create_jira_issues_from_structure(
            structure
        )

    return JSONResponse({
        "success": True,
        "structure": structure,
        "jira": jira_response
    })


@app.post("/modify")
async def modify(
    original_prompt: str = Form(...),
    modification_prompt: str = Form(...)
):

    updated = modify_sprint(
        original_prompt,
        modification_prompt
    )

    return JSONResponse({
        "success": True,
        "updated": updated
    })


# -----------------------------
# SLACK EVENTS
# -----------------------------

@app.post("/slack/events")
async def slack_events(request: Request):

    data = await request.json()

    if "challenge" in data:
        return JSONResponse({
            "challenge": data["challenge"]
        })

    event = data.get("event", {})

    if (
        event.get("type") == "message"
        and "bot_id" not in event
    ):

        user_id = event.get("user")
        text = event.get("text")
        channel_id = event.get("channel")

        # START STANDUP
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

        # OPEN AI ASSISTANT
        if text.lower() == "launch ai assistant":

            assistant_url = (
                "https://scrum-bot-bkaz.onrender.com/assistant"
            )

            client.chat_postMessage(
                channel=channel_id,
                text=f"Open AI Assistant: {assistant_url}"
            )

            return JSONResponse({"status": "assistant_sent"})

        # FOLLOWUP AI
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


# -----------------------------
# SLACK INTERACTIONS
# -----------------------------

@app.post("/slack/interactions")
async def slack_interactions(request: Request):

    form_data = await request.form()

    payload = json.loads(
        form_data["payload"]
    )

    channel_id = payload["channel"]["id"]

    action = payload["actions"][0]["action_id"]

    if action == "on_track_btn":

        reply = (
            "Great! What is your primary "
            "focus for today?"
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
```
