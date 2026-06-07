import requests


GAS_URL = "https://script.google.com/macros/s/AKfycbxyaw7C3fzCFkod69je6hLUE2EncogxoKQbwm7BQguZN20t7QB0UvOb2M_Zp4oFpuk/exec"


def fetch_today_plan():
    try:
        response = requests.get(GAS_URL, params={"action": "getTodayPlan"})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("❌ Failed to fetch today's plan:", e)
        return []


def mark_task_done(task_id):
    try:
        response = requests.post(GAS_URL, data={
            "action": "markTaskStatus",
            "task_id": task_id,
            "status": "Done"
        })
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("❌ Failed to update task:", e)
        return f"Error: {e}"


def fetch_watchlist():
    try:
        response = requests.get(GAS_URL, params={"action": "getWatchlist"})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("❌ Failed to fetch watchlist:", e)
        return []


def add_to_watchlist(item_description):
    try:
        response = requests.post(GAS_URL, data={
            "action": "addWatchlistItem",
            "item_description": item_description
        })
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("❌ Failed to add watchlist item:", e)
        return f"Error: {e}"


def mark_watchlist_item_watched(item_id):
    try:
        response = requests.post(GAS_URL, data={
            "action": "markWatchlistStatus",
            "item_id": item_id,
            "status": "Watched"
        })
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("❌ Failed to update watchlist item:", e)
        return f"Error: {e}"


def add_task_via_gemini(user_message):
    try:
        payload = {"message": user_message}
        response = requests.post(GAS_URL, data=payload)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("❌ Failed to add task via Gemini:", e)
        return f"❌ Error reaching task API: {str(e)}"
