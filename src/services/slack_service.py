import os
import slack_sdk
from src.services import email_service  # Assuming you have email_service.py
from src.services import llm_service  # Assuming you have llm_service.py
from src.config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD  # Assuming you have config.py

def send_slack_message(message):
    """Sends a message to a Slack channel."""
    try:
        slack_token = os.environ.get("SLACK_BOT_TOKEN")
        channel_id = os.environ.get("SLACK_CHANNEL_ID")

        if not slack_token or not channel_id:
            print("Slack token or channel ID not found in environment variables.")
            return False

        client = slack_sdk.WebClient(token=slack_token)
        response = client.chat_postMessage(channel=channel_id, text=message)

        if response["ok"]:
            print("Slack message sent successfully.")
            return True
        else:
            print(f"Error sending Slack message: {response['error']}")
            return False

    except Exception as e:
        print(f"Error sending Slack message: {e}")
        return False

def process_and_notify():
    """Fetches emails, analyzes them, and sends Slack notifications for important ones."""
    emails = email_service.fetch_emails_imap(IMAP_HOST, IMAP_USER, IMAP_PASSWORD)

    if emails:
        for email_data in emails:
            subject = email_data["subject"]
            sender = email_data["sender"]
            body = email_data["body"]

            # Analyze the email for importance (you can customize this logic)
            if "urgent" in body.lower() or "important" in subject.lower():
                summary = llm_service.summarize_email(body)
                if summary:
                    slack_message = f"🚨 *Important Email Alert!* 🚨\n\n*Subject:* {subject}\n*From:* {sender}\n\n*Summary:* {summary}"
                    send_slack_message(slack_message)
                else:
                    slack_message = f"🚨 *Important Email Alert!* 🚨\n\n*Subject:* {subject}\n*From:* {sender}\n\n*Body:* {body}"
                    send_slack_message(slack_message)

if __name__ == "__main__":
    process_and_notify()