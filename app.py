from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gas_client import (
    fetch_today_plan,
    mark_task_done,
    fetch_watchlist,
    add_to_watchlist,
    mark_watchlist_item_watched,
    add_task_via_gemini,
)

app = Flask(__name__)


def parse_comma_separated_ids(ids_raw):
    return [item_id.strip().lower() for item_id in ids_raw.split(",") if item_id.strip()]


def format_watchlist_item(item):
    status = item.get("status", "Pending")
    title = (
        item.get("title")
        or item.get("item_title")
        or item.get("item_description")
        or item.get("description")
        or item.get("name")
        or "Untitled"
    )
    item_type = item.get("type") or item.get("category")
    platform = item.get("platform") or item.get("where_to_watch")
    item_id = item.get("item_id") or item.get("watchlist_id") or item.get("id") or ""

    details = []
    if item_type:
        details.append(str(item_type))
    if platform:
        details.append(str(platform))
    if item_id:
        details.append(f"ID: {item_id}")

    detail_text = f" ({', '.join(details)})" if details else ""
    return f"- [{status}] {title}{detail_text}"

@app.route("/", methods=["GET"])
def home():
    return "A Life Well Lived WhatsApp Bot is running."

@app.route("/message", methods=["POST"])
def whatsapp_bot():
    raw_incoming_msg = request.values.get("Body", "").strip()
    incoming_msg = raw_incoming_msg.lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "today's plan" in incoming_msg or "what's my plan" in incoming_msg:
        plan = fetch_today_plan()
        if not plan:
            msg.body("No tasks found for today. Want me to add something?")
        else:
            text = "*Here's your plan for today:*\n"
            for task in plan:
                status = task.get("status", "Pending")
                desc = task.get("task_description", "No description")
                time = task.get("do_by_time", "No time")
                task_id = task.get("task_id", "")
                text += f"- [{status}] {desc} (Do by: {time}) — ID: {task_id}\n"
            msg.body(text)

    elif incoming_msg.startswith("done"):
        parts = incoming_msg.split(maxsplit=1)
        if len(parts) == 2:
            task_ids_raw = parts[1].strip()
            task_ids = parse_comma_separated_ids(task_ids_raw)

            if not task_ids:
                msg.body("Please provide at least one valid task ID (e.g., 'done T001, T002').")
            else:
                responses = []
                for task_id in task_ids:
                    result = mark_task_done(task_id)
                    responses.append(f"{task_id.upper()}: {result}")
                msg.body("\n".join(responses))
        else:
            msg.body("Please send: done TASK_ID (e.g., 'done T001') or multiple IDs like 'done T001, T002'")

    elif "watchlist" in incoming_msg and (
        incoming_msg.startswith("show")
        or incoming_msg.startswith("view")
        or incoming_msg.startswith("my")
        or incoming_msg in ["watchlist", "my watchlist"]
    ):
        watchlist = fetch_watchlist()
        if not watchlist:
            msg.body("Your watchlist is empty. Send 'add watchlist The Bear' to add something.")
        else:
            text = "*Here's your watchlist:*\n"
            for item in watchlist:
                text += f"{format_watchlist_item(item)}\n"
            msg.body(text)

    elif incoming_msg.startswith("watched"):
        parts = incoming_msg.split(maxsplit=1)
        if len(parts) == 2:
            item_ids = parse_comma_separated_ids(parts[1].strip())

            if not item_ids:
                msg.body("Please provide at least one valid watchlist ID (e.g., 'watched W001, W002').")
            else:
                responses = []
                for item_id in item_ids:
                    result = mark_watchlist_item_watched(item_id)
                    responses.append(f"{item_id.upper()}: {result}")
                msg.body("\n".join(responses))
        else:
            msg.body("Please send: watched ITEM_ID (e.g., 'watched W001') or multiple IDs like 'watched W001, W002'")

    elif incoming_msg.startswith("add watchlist") or incoming_msg.startswith("add to watchlist"):
        if incoming_msg.startswith("add to watchlist"):
            item_description = raw_incoming_msg[len("add to watchlist"):].strip()
        else:
            item_description = raw_incoming_msg[len("add watchlist"):].strip()

        if not item_description:
            msg.body("Please send what to add (e.g., 'add watchlist The Bear').")
        else:
            result = add_to_watchlist(item_description)
            msg.body(f"*Watchlist Add Result:*\n{result}")

    elif incoming_msg.startswith("add"):
        result = add_task_via_gemini(raw_incoming_msg)
        msg.body(f"*Task Add Result:*\n{result}")

    else:
        msg.body(
            "Hey! You can ask for:\n"
            "- 'Today's plan' to see your schedule\n"
            "- 'Done T001' to mark a task complete\n"
            "- 'Add walk at 7 AM tomorrow' to create a task\n"
            "- 'My watchlist' to see what you want to watch\n"
            "- 'Add watchlist The Bear' to add a watchlist item\n"
            "- 'Watched W001' to mark a watchlist item watched"
        )


    return str(resp)



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
