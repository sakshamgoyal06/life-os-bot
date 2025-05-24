import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_user_message(user_input):
    system_prompt = """
You are a helpful productivity assistant that helps users manage tasks through WhatsApp.

Your job is to understand the user's intent and return a structured JSON object. The possible actions are:
1. create_task
2. mark_task_done
3. unknown

Return a JSON object with:
- action: one of the above
- task_description: short description of task (if applicable)
- do_by_time: optional, in "HH:MM AM/PM" format
- date: optional, default to today (YYYY-MM-DD)
- task_id: only for mark_task_done
If the message is not task-related, return action: unknown.
"""

    today = datetime.now().strftime('%Y-%m-%d')

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2
        )
        reply = response.choices[0].message['content']
        return reply
    except Exception as e:
        return f"Error: {e}"
