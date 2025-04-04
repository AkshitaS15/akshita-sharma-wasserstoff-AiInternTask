# src/utils/email_utils.py
import email
from email.header import decode_header
import base64

def extract_email_data_imap(msg):
    try:
        sender = str(decode_header(msg.get("From"))[0][0])
        recipient = str(decode_header(msg.get("To"))[0][0])
        subject = str(decode_header(msg.get("Subject"))[0][0])
        timestamp = str(msg.get("Date"))
        body = get_email_body_imap(msg)
        return {"sender": sender, "recipient": recipient, "subject": subject, "timestamp": timestamp, "body": body}
    except Exception as e:
        print(f"Error extracting email data: {e}")
        return None

def get_email_body_imap(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode()
            elif content_type == "text/html" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode()
    elif msg.get_content_type() == "text/plain":
        return msg.get_payload(decode=True).decode()
    elif msg.get_content_type() == "text/html":
        return msg.get_payload(decode=True).decode()
    return ""