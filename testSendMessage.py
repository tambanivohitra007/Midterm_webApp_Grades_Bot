import logging
import requests
import msal
from config import TENANT_ID, CLIENT_ID, INSTRUCTOR_EMAIL, STUDENT_EMAILS

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Chat.ReadWrite"]
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def get_access_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if not result:
        result = app.acquire_token_interactive(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Failed to acquire token.")


def send_test_message(student_email, instructor_email, headers):
    # Sample grade text with bullet points and spacing
    grade_text = "\n".join([
        "Assignment 1: 85%",
        "Assignment 2: 90%",
        "Final Project: 92%",
        "Overall Grade: A"
    ])

    # Format with bullet points
    formatted_text = "\n".join([f"- {line}" for line in grade_text.splitlines()])

    message = f"""
    <p><strong>Hello sfqsdfdfdf,</strong></p>
    <p>Here is your grade report:</p>
    <ul>
        <li>Assignment 1: 85%</li>
        <li>Assignment 2: 90%</li>
        <li>Final Project: 92%</li>
        <li>Overall Grade: A</li>
    </ul>
    <p>Regards,<br>Your Instructor</p>
    """

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
        logging.error(f"Failed to create chat: {chat_resp.text}")
        return

    chat_id = chat_resp.json()["id"]
    msg_payload = {"body": {"contentType": "html", "content": message}}
    msg_resp = requests.post(f"{GRAPH_URL}/chats/{chat_id}/messages", headers=headers, json=msg_payload)

    if msg_resp.status_code in [200, 201]:
        logging.info("✅ Test message sent successfully.")
    else:
        logging.error(f"❌ Failed to send test message: {msg_resp.text}")


def main():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    test_student_email = list(STUDENT_EMAILS.values())[0]  # Send to yourself for preview
    send_test_message(test_student_email, INSTRUCTOR_EMAIL, headers)


if __name__ == "__main__":
    main()