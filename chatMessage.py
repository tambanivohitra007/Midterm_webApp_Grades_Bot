import os
import time
import logging
import requests
import msal
import sys
from config import (
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    INSTRUCTOR_EMAIL,
    STUDENT_EMAILS,
    OUTPUT_DIR
)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Chat.ReadWrite"]  # Delegated permissions

STUDENT_REPOS_PATH = OUTPUT_DIR

GRAPH_URL = "https://graph.microsoft.com/v1.0"

# =========================
# LOGGING SETUP
# =========================

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("teams_grade_log.txt", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# =========================
# FUNCTIONS
# =========================

def get_access_token():
    """Interactive login as instructor (desktop/public client)."""
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

    # Try to get token silently from cache
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        logging.info("🪪 Logging in interactively — please complete sign-in in your browser...")
        result = app.acquire_token_interactive(scopes=SCOPES)

    if "access_token" in result:
        logging.info("✅ Successfully acquired access token (delegated).")
        return result["access_token"]
    else:
        logging.error("❌ Failed to get access token.")
        logging.error(result.get("error_description"))
        raise Exception("Failed to acquire token.")


def send_message_to_user(student_email, instructor_email, message, headers):
    """Create a 1:1 chat (signed-in instructor + student) and send message."""
    chat_payload = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{instructor_email}')"
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{student_email}')"
            }
        ]
    }

    chat_resp = requests.post(f"{GRAPH_URL}/chats", headers=headers, json=chat_payload)
    if chat_resp.status_code not in [200, 201]:
        logging.error(f"❌ Failed to create chat: {chat_resp.text}")
        return False

    chat_id = chat_resp.json()["id"]

    msg_payload = {"body": {"contentType": "text", "content": message}}
    msg_resp = requests.post(f"{GRAPH_URL}/chats/{chat_id}/messages", headers=headers, json=msg_payload)

    if msg_resp.status_code in [200, 201]:
        logging.info(f"📨 Message sent to {student_email}")
        return True
    else:
        logging.error(f"❌ Failed to send message: {msg_resp.text}")
        return False


def main():
    logging.info("🚀 Starting grade sending process...")
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for student_folder, student_email in STUDENT_EMAILS.items():
        grade_path = os.path.join(STUDENT_REPOS_PATH, student_folder, "result.txt")

        if not os.path.exists(grade_path):
            logging.warning(f"⚠ No result.txt found for {student_folder}. Skipping.")
            continue

        try:
            with open(grade_path, "r", encoding="utf-8", errors="replace") as f:
                grade_text = f.read().strip()
        except Exception as e:
            logging.error(f"❌ Error reading grade file for {student_folder}: {e}")
            continue

        message = (
            f"Hello {student_folder},\n\n"
            f"Here is your grade report:\n\n{grade_text}\n\n"
            f"Regards,\nYour Instructor"
        )

        success = send_message_to_user(
            student_email=student_email,
            instructor_email=INSTRUCTOR_EMAIL,
            message=message,
            headers=headers
        )

        if success:
            logging.info(f"✅ Successfully sent grade to {student_folder} ({student_email})")
        else:
            logging.error(f"❌ Failed to send grade to {student_folder} ({student_email})")

        time.sleep(1)  # Avoid throttling

    logging.info("🏁 Grade sending process completed.")


if __name__ == "__main__":
    main()