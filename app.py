from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gas_client import fetch_today_plan, mark_task_done  # existing functions
from gpt_client import parse_user_message  # NEW
import json
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "A Life Well Lived WhatsApp Bot is running."

@app.route("/message", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "").strip()
    print("User said:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    try:
        # Interpret message with GPT
        gpt_reply = parse_user_message(incoming_msg)
        print("GPT response:", gpt_reply)

        parsed = json.loads(gpt_reply)
        action = parsed.get("action")

        if action == "create_task":
            desc = parsed.get("task_description", "No description")
            time = parsed.get("do_by_time", "anytime")
            date = parsed.get("date", "")
            # TODO: Hook into create_task() via Apps Script
            msg.body(f"Got it! I’ll add: *{desc}* (by {time}) on {date or 'today'}.")

        elif action == "mark_task_done":
            task_id = parsed.get("task_id")
            if task_id:
                result = mark_task_done(task_id)
                msg.body(result)
            else:
                msg.body("I couldn’t find a task ID to mark as done.")

        elif action == "unknown":
            msg.body("Hmm, I didn’t quite get that. Try saying something like:\n- 'Add gym at 6 PM'\n- 'Done T002'")

        else:
            msg.body("Not sure how to process that yet. Want to try again?")

    except Exception as e:
        print("Error:", e)
        msg.body("Oops! Something broke while interpreting your message. Try again later.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
