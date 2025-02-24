from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import os
from dotenv import load_dotenv
import re

dotenv_path = os.path.abspath("../AiScheduler/AiScheduler/.env")
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
if not FIREBASE_CREDENTIALS_PATH:
    raise ValueError("❌ FIREBASE_CREDENTIALS_PATH is missing from .env!")

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

api_key = os.getenv("SAMBANOVA_API_KEY")
base_url = os.getenv("SAMBANOVA_BASE_URL")
APIModel = os.getenv("")
client = openai.OpenAI(api_key=api_key, base_url=base_url)

# ✅ Store Pending Requests
pending_requests = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get("user_id", "")
    user_message = data.get("message", "")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # Retrieve full timetable history
        timetable_ref = db.collection("timetables").document(user_id).collection("dates")
        timetable_docs = timetable_ref.stream()

        full_timetable_history = {}
        for doc in timetable_docs:
            full_timetable_history[doc.id] = doc.to_dict()

        print("📅 Full Timetable History:", json.dumps(full_timetable_history, indent=2))

        timetable_history_str = json.dumps(full_timetable_history)

        # ✅ Check if user is confirming a conflict resolution
        user_replying_to_conflict = False
        if user_id in pending_requests:
            if user_message.strip().upper() == "YES":
                user_replying_to_conflict = True
                original_request = pending_requests[user_id]
                print("🔄 Restoring Original Request:", original_request)

                # ✅ Modify user_message to force AI to replace instead of detecting conflict again
                user_message = f"User confirmed replacement. Replace {original_request}."

                # Prevent infinite conflict loop
                del pending_requests[user_id]  

        response = client.chat.completions.create(
            model=APIModel,
            messages=[
                {"role": "system", "content": 
f"📅 **You are an AI scheduling assistant.**\n\n"
"🔥 **CRITICAL RULE: RETURN ONLY JSON. NO EXTRA TEXT.**\n"
"- **All responses MUST be a single valid JSON object.**\n"
"- **DO NOT return explanations, reasoning, markdown, or comments.**\n"
"\n"
"🔍 **Time Conflict Check (Firebase Validation Only)**\n"
"- **Convert all times into 24-hour format for accurate checking.**\n"
"- **A conflict exists if:**\n"
"  - (`new_event_start` < `existing_event_end`) AND (`new_event_end` > `existing_event_start`)\n"
"\n"
"📜 **Timetable History (Firebase Firestore, Use This Data):**\n"
f"{timetable_history_str}\n"
"\n"
"📌 **User's Scheduling Request:**\n"
'  {\n'
'    "updates": { "date": "[User Requested Date]", "subject": "[User Requested Subject]", "time": "[User Requested Start Time]", "duration": "[User Requested Duration]" }\n'
'  }\n'
"\n"
"⚠️ **Conflict Resolution Rules:**\n"
"- **If NO conflict exists, schedule the event immediately.**\n"
"- **If a conflict exists, return JSON as:**\n"
'  {\n'
'    "message": "A conflict exists with [Event Name] on [Date] from [Start Time] to [End Time]. Do you want to replace it? (YES/NO)",\n'
'    "updates": {}  # Keep empty until user confirms\n'
'  }\n'
"- **If user confirms with YES, IMMEDIATELY replace the event and return:**\n"
'  {\n'
'    "message": "Event replaced successfully.",\n'
'    "updates": { "date": "[Date]", "subject": "[New Subject]", "time": "[Start Time]", "duration": "[Duration]" }\n'
'  }\n'
"\n"
"🚨 **STRICT JSON RESPONSE FORMAT ONLY.** 🚨\n"
"🔄 **Duration Format Rule:**\n"
"- **Always return durations in hour format:**\n"
"  - ✅ `0.5 hours`, `1 hour`, `1.5 hours`, `2 hours`\n"
"  - ❌ Do NOT use minutes (e.g., 30 min, 60 min, etc.)\n"
},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            top_p=0.1
        )

        raw_text = response.choices[0].message.content.strip()
        print("🤖 Raw AI Message Content:", raw_text)

        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(0)

        try:
            ai_output = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print("❌ JSON Parsing Error:", e)
            return jsonify({"message": "AI is having trouble understanding. Please retype your request.", "updates": {}})

        ai_output.setdefault("message", "Invalid response format.")
        ai_output.setdefault("updates", {})

        # 🛑 If conflict detected, store the original request
        if not ai_output["updates"]:
            if "A conflict exists" in ai_output["message"]:
                pending_requests[user_id] = user_message
            return jsonify(ai_output)

        # ✅ Store Updates in Firestore
        updates = ai_output["updates"]
        event_date = updates.get("date", "")
        event_subject = updates.get("subject", "")
        event_time = updates.get("time", "")
        event_duration = updates.get("duration", "")

        if event_date and event_subject and event_time and event_duration:
            date_ref = db.collection("timetables").document(user_id).collection("dates").document(event_date)

            existing_data = date_ref.get().to_dict() or {}
            existing_updates = existing_data.get("updates", [])

            # ✅ Remove conflicted event
            existing_updates = [e for e in existing_updates if e["time"] != event_time]

            # ✅ Add new event
            existing_updates.append({
                "date": event_date,
                "subject": event_subject,
                "time": event_time,
                "duration": event_duration
            })

            date_ref.set({"updates": existing_updates}, merge=True)

        return jsonify(ai_output)

    except Exception as e:
        print("❌ Flask Error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
