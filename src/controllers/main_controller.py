import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)
import sqlite3
import json
from src.services import email_service
from src.services import llm_service
from src.services import web_search_service
from src.services import slack_service
from src.services import calendar_service
from src.utils import db_utils
from src.config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD, DB_PATH

def execute_query(conn, query, params=None):
    """Executes a database query with error handling."""
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None

def fetch_one(cursor):
    """Fetches one result from a cursor with error handling."""
    try:
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database Error (fetch one): {e}")
        return None

def fetch_all(cursor):
    """Fetches all results from a cursor with error handling."""
    try:
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database Error (fetch all): {e}")
        return None

# --- Main Controller ---
def main():
    emails = email_service.fetch_emails_imap(IMAP_HOST, IMAP_USER, IMAP_PASSWORD)
    if emails:
        for email_data in emails:
            process_email(email_data)
    else:
        print("No emails to display.")

def process_email(email_data):
    """Processes a single email, extracting information and performing actions."""

    print("-" * 40)  # Separator for each email
    print(f"Subject: {email_data['subject']}")
    print(f"From: {email_data['sender']}")

    # --- LLM Services ---
    summary = llm_service.summarize_email(email_data["body"])
    if summary:
        print(f"Summary: {summary}")

    intent = llm_service.infer_intent(email_data["body"])
    if intent:
        print(f"Intent: {intent}")

    # --- Database Storage ---
    db_utils.store_email_in_db(email_data, DB_PATH)  # Assuming this is already robust

    # --- Web Search ---
    if "search" in email_data["body"].lower():
        search_result = web_search_service.web_search("example search")  # Replace with dynamic query
        if search_result:
            print(f"Search result: {search_result}")

    # --- Reply Drafting ---
    draft_and_save_reply(email_data)

    # --- Meeting Extraction and Calendar Scheduling ---
    handle_meeting_scheduling(email_data)

    # --- Slack Notification ---
    if "urgent" in email_data["body"].lower():
        slack_result = slack_service.send_slack_message(email_data["body"])
        print(slack_result)

def draft_and_save_reply(email_data):
    """Drafts a reply using the LLM and saves it as a draft."""

    reply = llm_service.draft_reply(email_data["body"])
    if reply:
        print(f"Draft reply: {reply}")
        try:
            with email_service.imaplib.IMAP4_SSL(IMAP_HOST) as imap_conn:
                imap_conn.login(IMAP_USER, IMAP_PASSWORD)
                imap_conn.select('INBOX')
                email_service.save_draft(imap_conn, email_data["sender"], f"Re: {email_data['subject']}", reply)
                print("Draft saved successfully.")
        except email_service.imaplib.IMAP4.error as e:
            print(f"Error saving draft: {e}")
        except Exception as e:
            print(f"Unexpected error during draft saving: {e}")

def handle_meeting_scheduling(email_data):
    """Extracts meeting details and schedules a calendar event."""

    print("Email Body being sent to LLM for meeting extraction:")
    print(email_data["body"])
    meeting_details_json = llm_service.extract_meeting_details(email_data["body"])
    print(f"LLM Meeting Details JSON: {meeting_details_json}")

    if meeting_details_json:
        try:
            meeting_details = json.loads(meeting_details_json)
            if meeting_details:
                date_str = meeting_details.get("date")
                time_str = meeting_details.get("time")
                title = meeting_details.get("title", "Meeting")
                time_zone = meeting_details.get("timeZone", "America/Los_Angeles")

                print(f"Extracted Date: {date_str}, Time: {time_str}, TimeZone: {time_zone}")

                if date_str and time_str:
                    event_details = {
                        "title": title,
                        "date": date_str,
                        "time": time_str,
                        "timeZone": time_zone
                    }
                    event_result = calendar_service.schedule_event(calendar_service.get_calendar_id(), event_details)
                    print(event_result)

                    share_calendar_if_needed(email_data["sender"])  # Moved calendar sharing here
                else:
                    print("Incomplete meeting details found, skipping calendar event creation.")
            else:
                print("LLM returned empty meeting details JSON.")

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from LLM: {meeting_details_json}")
            print(f"JSONDecodeError details: {e}")
        except Exception as e:
            print(f"Error scheduling meeting: {e}")
    else:
        print("LLM did not return any meeting details JSON.")

def share_calendar_if_needed(sender_email):
    """Shares the calendar if it hasn't been shared with the sender before."""

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = execute_query(conn, "SELECT calendar_shared FROM emails WHERE sender = ?", (sender_email,))
        if not cursor:
            return  # Exit if query failed

        result = fetch_one(cursor)
        calendar_shared = result[0] if result else 0

        if not calendar_shared:
            calendar_service.share_calendar(calendar_service.get_calendar_id(), "guestacc.jan12000@gmail.com")
            execute_query(conn, "UPDATE emails SET calendar_shared = 1 WHERE sender = ?", (sender_email,))
            conn.commit()
            print(f"Calendar shared with {sender_email}")
        else:
            print(f"Calendar already shared with {sender_email}")

    finally:
        conn.close()

if __name__ == "__main__":
    # Add the project's root directory to sys.path (if not already handled)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

    main()