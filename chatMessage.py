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
SCOPES = ["User.Read", "Chat.ReadWrite"]

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
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if not result:
        logging.info("Logging in interactively — please complete sign-in in your browser...")
        result = app.acquire_token_interactive(scopes=SCOPES)
    if "access_token" in result:
        logging.info("Successfully acquired access token (delegated).")
        return result["access_token"]
    else:
        logging.error("Failed to get access token.")
        logging.error(result.get("error_description"))
        raise Exception("Failed to acquire token.")


def send_message_to_user(student_email, instructor_email, message_html, headers):
    # Create or get existing chat
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
        return False

    chat_id = chat_resp.json()["id"]

    # Check if message is extremely large and needs to be split
    max_single_message = 28000
    if len(message_html) > max_single_message:
        logging.warning(f"Message too large ({len(message_html)} chars), attempting to split into multiple messages")
        return send_split_messages(chat_id, message_html, headers, student_email)

    # Send single message
    msg_payload = {
        "body": {
            "contentType": "html",
            "content": message_html
        }
    }

    msg_resp = requests.post(f"{GRAPH_URL}/chats/{chat_id}/messages", headers=headers, json=msg_payload)

    if msg_resp.status_code in [200, 201]:
        logging.info(f"Message sent to {student_email}")
        return True
    else:
        logging.error(f"Failed to send message: {msg_resp.text}")
        return False


def send_split_messages(chat_id, message_html, headers, student_email):
    """Split a large message into multiple smaller messages"""
    import re

    # Try to split at milestone boundaries
    milestones = re.findall(r'<div class="milestone">.*?</div>', message_html, re.DOTALL)

    if len(milestones) > 1:
        # Send header message first
        header_match = re.search(r'^(.*?)<div class="milestone">', message_html, re.DOTALL)
        if header_match:
            header_content = header_match.group(1)
            if not send_single_message(chat_id, header_content, headers):
                return False

        # Send each milestone as separate message
        for i, milestone in enumerate(milestones):
            milestone_msg = f"""
            <div style="font-family:'Segoe UI', Arial, sans-serif; font-size:13px; color:#2b2b2b;">
                <div style="background:#f0f7ff; padding:15px; border-radius:8px; margin-bottom:15px; border-left:4px solid #007acc;">
                    <h3 style="margin:0; color:#007acc;">Part {i + 1} of {len(milestones)}</h3>
                </div>
                {milestone}
            </div>
            """
            if not send_single_message(chat_id, milestone_msg, headers):
                logging.error(f"Failed to send milestone {i + 1}")
                return False
            time.sleep(1)  # Small delay between messages

        # Send footer/summary if it exists
        footer_match = re.search(r'</div>\s*(<div class="final-grade">.*?)$', message_html, re.DOTALL)
        if footer_match:
            footer_content = f"""
            <div style="font-family:'Segoe UI', Arial, sans-serif; font-size:13px; color:#2b2b2b;">
                {footer_match.group(1)}
            </div>
            """
            if not send_single_message(chat_id, footer_content, headers):
                return False

        logging.info(f"Successfully sent split messages to {student_email}")
        return True
    else:
        # Can't split meaningfully, try to send as is
        logging.warning(f"Cannot split message meaningfully, attempting to send large message anyway")
        return send_single_message(chat_id, message_html, headers)


def send_single_message(chat_id, content, headers):
    """Send a single message to a chat"""
    msg_payload = {
        "body": {
            "contentType": "html",
            "content": content
        }
    }

    msg_resp = requests.post(f"{GRAPH_URL}/chats/{chat_id}/messages", headers=headers, json=msg_payload)
    return msg_resp.status_code in [200, 201]


def build_html_message(student_name, grade_html_content, force_condensed=False, compress_html=True):
    # Since grade_html_content is already HTML, we need to extract the body content
    # and wrap it in a Teams-friendly format

    import re

    # Extract the body content from the HTML (remove <html>, <head>, etc.)
    body_match = re.search(r'<body>(.*?)</body>', grade_html_content, re.DOTALL)
    if body_match:
        grade_body = body_match.group(1).strip()
    else:
        # Fallback: use the entire content if no body tag found
        grade_body = grade_html_content.strip()

    # Since students don't have access to result.html, we need to send complete content through Teams
    # Teams supports scrolling and has a practical limit around 28KB
    # Let's optimize the HTML for Teams while preserving ALL content

    max_length = 28000  # Teams practical limit

    # Apply HTML compression if enabled
    if compress_html:
        import re
        original_length = len(grade_body)

        # Remove excessive whitespace while preserving readability
        grade_body = re.sub(r'\n\s+', '\n', grade_body)  # Remove indentation
        grade_body = re.sub(r'\s+', ' ', grade_body)  # Collapse multiple spaces
        grade_body = re.sub(r'>\s+<', '><', grade_body)  # Remove spaces between tags

        compressed_length = len(grade_body)
        if original_length != compressed_length:
            logging.info(
                f"HTML compressed from {original_length} to {compressed_length} characters ({((original_length - compressed_length) / original_length * 100):.1f}% reduction)")

    # Add guidance notice for large reports
    if len(grade_body) > 20000:  # Large but manageable
        grade_body = f'''
        <div style="background-color:#fff3cd; padding:15px; border-radius:8px; border-left:4px solid #ffc107; margin-bottom:20px;">
            <h3 style="margin-top:0; color:#856404;">📋 Large Report Notice</h3>
            <p><strong>This is a comprehensive grade report.</strong> For the best experience:</p>
            <ul style="margin:10px 0;">
                <li>Use <strong>vertical scrolling</strong> to navigate through sections</li>
                <li>Take your time reading each milestone's feedback</li>
                <li>Use the Teams desktop app for optimal performance</li>
            </ul>
        </div>
        {grade_body}
        '''

    # Always add scrolling guidance for any report
    grade_body = f'''
    <div style="background-color:#e8f5e8; padding:15px; border-radius:8px; border-left:4px solid #4caf50; margin-bottom:25px;">
        <h3 style="margin-top:0; color:#2e7d32;">📋 Complete Grade Report</h3>
        <p>This report contains your complete grading details. <strong>Scroll vertically</strong> to view all sections including individual milestone feedback.</p>
    </div>
    {grade_body}
    '''

    return f"""
    <div style="font-family:'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size:13px; line-height:1.5; color:#2b2b2b; max-width:100%; overflow-x:hidden;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:20px; border-radius:12px; margin-bottom:25px; text-align:center;">
            <h1 style="margin:0; font-size:24px; font-weight:600;">Midterm Project</h1>
            <h2 style="margin:5px 0 0 0; font-size:18px; font-weight:400; opacity:0.9;">Grade Report</h2>
            <p style="margin:8px 0 0; font-size:14px; opacity:0.8;">Muaklek Campus</p>
        </div>

        <div style="background:#ffffff; padding:25px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.1); margin-bottom:20px;">
            <p style="margin:0 0 15px 0; font-size:16px;"><strong>Hello {student_name},</strong></p>
            <p style="margin:0; color:#666; font-size:14px;">Please find your detailed grade report below. You can scroll vertically to view all sections.</p>
        </div>

        <div style="background:#ffffff; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.1); overflow:hidden;">
            <div style="padding:25px; max-height:none; overflow-y:visible;">
                {grade_body}
            </div>
        </div>

        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:20px; border-radius:12px; margin-top:25px; text-align:center;">
            <p style="margin:0 0 10px 0; font-size:16px; font-weight:600;">Best regards,</p>
            <p style="margin:0 0 15px 0; font-size:14px;">Mr. Rindra</p>
            <p style="margin:0; font-size:12px; opacity:0.8;">Sent automatically via Microsoft Teams</p>
        </div>

        <div style="text-align:center; margin-top:20px; padding:15px; background:#f8f9fa; border-radius:8px;">
            <p style="margin:0; font-size:12px; color:#666;">💡 <strong>Tip:</strong> For the best viewing experience, scroll slowly through each section of your report.</p>
        </div>
    </div>
    """


def main():
    logging.info("Starting grade sending process...")
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    successful_sends = 0
    total_students = len(STUDENT_EMAILS)

    # Configuration options for handling large reports
    force_condensed = False  # Set to True to force condensed summaries for all reports
    allow_message_splitting = True  # Set to True to allow splitting large reports into multiple messages
    compress_html = True  # Set to True to compress HTML for better Teams compatibility

    for student_folder, student_email in STUDENT_EMAILS.items():
        logging.info(f"Processing {student_folder} ({student_email})...")
        grade_path = os.path.join(STUDENT_REPOS_PATH, student_folder, "result.html")

        if not os.path.exists(grade_path):
            logging.warning(f"No result.html found for {student_folder} at {grade_path}. Skipping.")
            continue

        try:
            with open(grade_path, "r", encoding="utf-8", errors="replace") as f:
                grade_content = f.read().strip()

            if not grade_content:
                logging.warning(f"Empty grade file for {student_folder}. Skipping.")
                continue

            logging.info(f"Read grade file for {student_folder}: {len(grade_content)} characters")

        except Exception as e:
            logging.error(f"Error reading grade file for {student_folder}: {e}")
            continue

        try:
            message_html = build_html_message(student_folder, grade_content, force_condensed, compress_html)
            logging.info(f"Built HTML message for {student_folder}: {len(message_html)} characters")

            # Check if we should allow message splitting for very large content
            if not allow_message_splitting and len(message_html) > 28000:
                logging.warning(
                    f"Message is {len(message_html)} characters but splitting is disabled. May fail to send.")
            elif allow_message_splitting and len(message_html) > 28000:
                logging.info(f"Large message will be split into multiple parts for better delivery.")

            success = send_message_to_user(
                student_email=student_email,
                instructor_email=INSTRUCTOR_EMAIL,
                message_html=message_html,
                headers=headers
            )

            if success:
                successful_sends += 1
                logging.info(
                    f"Successfully sent grade to {student_folder} ({student_email}) [{successful_sends}/{total_students}]")
            else:
                logging.error(f"Failed to send grade to {student_folder} ({student_email})")

        except Exception as e:
            logging.error(f"Error processing {student_folder}: {e}")

        # Add delay between sends to avoid rate limiting
        time.sleep(2)

    logging.info(
        f"Grade sending process completed. Successfully sent {successful_sends}/{total_students} grade reports.")


if __name__ == "__main__":
    main()