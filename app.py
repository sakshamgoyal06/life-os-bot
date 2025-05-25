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
                task_id = task.get("task_id", "")
                text += f"- [{status}] {desc} (Do by: {time}) — ID: {task_id}\n"
            msg.body(text)

    elif incoming_msg.startswith("done"):
        parts = incoming_msg.split(maxsplit=1)
        if len(parts) == 2:
            task_ids_raw = parts[1].strip()
            task_ids = [tid.strip().lower() for tid in task_ids_raw.split(",") if tid.strip()]
            
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

    else:
        msg.body(
            "Hey! You can ask for:\n"
            "- 'Today's plan' to see your schedule\n"
            "- 'Done T001' to mark a task complete\n"
            "- 'Done T001, T002' to mark multiple tasks"
        )

    return str(resp)



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
