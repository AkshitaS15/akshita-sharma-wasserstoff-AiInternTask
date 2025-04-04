# src/services/email_service.py

import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup  # Make sure to install this: pip install beautifulsoup4
import google.generativeai as genai  # Make sure to install this: pip install google-generativeai
from src.config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD, GOOGLE_API_KEY  # Import your config
import os
from googleapiclient.discovery import build  # Unused in this version
from google.oauth2 import service_account  # Might not be needed
import datetime
import os
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.0-flash'  # <---- IMPORTANT:  Verify this model name!

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
SCOPES = ['https://www.googleapis.com/auth/calendar']
#SERVICE_ACCOUNT_FILE = 'path/to/your/service-account.json' # Not used in IMAP draft saving

def clean_text(text):
    """Removes HTML tags and special characters."""
    return BeautifulSoup(text, "html.parser").get_text()

def get_email_body(msg):
    """Extracts the email body (text or HTML)."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                body = part.get_payload(decode=True).decode()
            except:
                continue
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return body
            elif content_type == "text/html" and "attachment" not in content_disposition:
                return clean_text(body)
    else:
        return clean_text(msg.get_payload(decode=True).decode())

def is_interview_related(email_body):
    """Determines if an email is related to an interview scheduling."""
    keywords = ["interview", "schedule", "availability", "meeting", "discussion"]
    return any(keyword in email_body.lower() for keyword in keywords)

def check_availability():
    """Checks available time slots (mock function)."""
    return "Available slots: Monday 10 AM - 12 PM, Wednesday 2 PM - 4 PM."

def generate_ai_response(email_body, sender_name, sender_email):
    """Generates an AI response using the Gemini API."""
    if is_interview_related(email_body):
        availability = check_availability()
        prompt = f"""You are an AI assistant responding to interview scheduling requests.
        The sender is {sender_name} ({sender_email}).
        Email Body:
        {email_body}

        Your response should confirm availability and suggest open time slots.
        Available Slots:
        {availability}

        Draft Reply:
        """
    else:
        prompt = f"""You are an intelligent assistant drafting email replies.
        The Sender's name is {sender_name} and the email is {sender_email}.
        Email Body:
        {email_body}

        Draft Reply:
        """

    try:
        model = genai.GenerativeModel(MODEL_NAME, safety_settings=SAFETY_SETTINGS)
        response = model.generate_content(prompt)
        return f"{response.text}\n\nRegards,\nYour Name"
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return None
def save_draft(imap, recipient, subject, body):
    """Saves the AI-generated response as a draft using IMAP."""
    try:
        print("Starting save_draft function...")
        # Create a MIME email message
        msg = MIMEMultipart()
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html", "utf-8"))  # Set the email content

        # Convert email to bytes
        raw_email = msg.as_string().encode("utf-8")
        print(f"Raw email created: {raw_email[:100]}...") # print first 100 char of raw email

        # Define Drafts folder
        drafts_folder = "[Gmail]/Drafts"
        print(f"Drafts folder: {drafts_folder}")

        # Append email to Drafts folder
        result, data = imap.append(drafts_folder, None, None, raw_email)
        print(f"IMAP append result: {result}, data: {data}")

        print(f"✅ Draft saved for: {recipient}")

    except Exception as e:
        print(f"❌ Error saving draft: {e}")

def process_emails():
    """Fetches unread emails, generates responses, and saves them as drafts."""
    imap = None
    try:
        print("Starting process_emails function...")
        # Connect to the IMAP server using imaplib
        imap = imaplib.IMAP4_SSL(IMAP_HOST)
        print(f"IMAP connection: {imap}")
        imap.login(IMAP_USER, IMAP_PASSWORD)
        print("IMAP login successful.")
        imap.select('INBOX')
        print("INBOX selected.")

        # Search for unread emails
        status, messages = imap.search(None, 'SEEN') # or UNSEEN
        if status == 'OK':
            msg_ids = messages[0].split()
            print(f"Found {len(msg_ids)} emails.")
            for msgid in msg_ids:
                try:
                    print(f"Processing message ID: {msgid}")
                    status, msg_data = imap.fetch(msgid, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        sender_email = msg["from"]
                        sender_name = decode_header(msg["from"])[0][0]
                        if isinstance(sender_name, bytes):
                            sender_name = sender_name.decode()
                        subject = msg["subject"]
                        if subject:
                            subject = decode_header(subject)[0][0]
                            if isinstance(subject, bytes):
                                subject = subject.decode()
                        email_body = get_email_body(msg)
                        ai_response = generate_ai_response(email_body, sender_name, sender_email)
                        if ai_response:
                            print(f"Generated AI response: {ai_response[:100]}...")
                            save_draft(imap, sender_email, f"Re: {subject}", ai_response)
                except Exception as inner_e:
                    print(f"Error processing message ID {msgid}: {inner_e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if imap:
            try:
                imap.close()
                imap.logout()
            except Exception as logout_error:
                print(f"Error during logout: {logout_error}")
        print("process_emails() finished")
def fetch_emails_imap(host, user, password, mailbox="INBOX", num_emails=5):
    """Fetches emails from IMAP."""
    try:
        mail = imaplib.IMAP4_SSL(host)
        mail.login(user, password)
        mail.select(mailbox)
        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()
        emails = []
        for i in mail_ids[-num_emails:]:
            _, data = mail.fetch(i, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_data = extract_email_data_imap(msg)
                    if email_data:
                        emails.append(email_data)
        mail.close()
        mail.logout()
        return emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def extract_email_data_imap(msg):
    try:
        sender = str(decode_header(msg.get("From"))[0][0])
        recipient = str(decode_header(msg.get("To"))[0][0])
        subject = str(decode_header(msg.get("Subject"))[0][0])
        timestamp = str(msg.get("Date"))
        body = get_email_body(msg)
        return {"sender": sender, "recipient": recipient, "subject": subject, "timestamp": timestamp, "body": body}
    except Exception as e:
        print(f"Error extracting email data: {e}")
        return None