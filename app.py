from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gas_client import fetch_today_plan, mark_task_done

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "A Life Well Lived WhatsApp Bot is running."

@app.route("/message", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
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
                text += f"- [{status}] {desc} (Do by: {time})\n"
            msg.body(text)

    elif incoming_msg.startswith("done"):
        parts = incoming_msg.split()
        if len(parts) == 2:
            task_id = parts[1].strip().upper()
            result = mark_task_done(task_id)
            msg.body(result)
        else:
            msg.body("Please send: done TASK_ID (e.g., 'done T001')")

    else:
        msg.body(
            "Hey! You can ask for:\n"
            "- 'Today's plan' to see your schedule\n"
            "- 'Done T001' to mark a task complete"
        )

    return str(resp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
