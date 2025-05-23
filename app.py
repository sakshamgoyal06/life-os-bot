
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.lower() == "hi":
        msg.body("👋 Hey Saksham! I'm your Life OS. Ready to plan today?")
    else:
        msg.body(f"✅ Noted: '{incoming_msg}' – I'll track that for you.")

    return str(resp)

if __name__ == "__main__":
    app.run()
