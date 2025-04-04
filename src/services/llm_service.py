# src/llm_service.py
import google.generativeai as genai
from src.config import GOOGLE_API_KEY
import json
import re 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def summarize_email(email_body):
    try:
        prompt = f"Summarize the following email:\n\n{email_body}\n\nSummary:"
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else None
    except Exception as e:
        print(f"Error summarizing email: {e}")
        return None

def infer_intent(email_body):
    try:
        prompt = f"What is the main intent of this email?\n\n{email_body}\n\nIntent:"
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else None
    except Exception as e:
        print(f"Error inferring intent: {e}")
        return None

def draft_reply(email_body):
    try:
        prompt = f"Draft a polite and concise reply to:\n\n{email_body}\n\nReply:"
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else None
    except Exception as e:
        print(f"Error drafting reply: {e}")
        return None
# llm_service.py
def extract_meeting_details(email_body):
    """Extracts meeting details from an email using the LLM."""
    try:
        prompt = f"""
        You are an assistant that extracts meeting details from emails for calendar scheduling.
        Extract the NEW meeting date, time, title, and timezone from the following email.
        Return the result in JSON format with the keys: "date", "time", "title", "timeZone".
        If no meeting is mentioned, or if the email is only a rescheduling request, extract the NEW meeting details.

        Example 1:
        Email: "Let's meet on April 15th at 2 PM to discuss the project. The meeting title is 'Project Discussion'."
        JSON: {{"date": "2025-04-15", "time": "14:00", "title": "Project Discussion", "timeZone": "Asia/Kolkata"}}

        Example 2:
        Email: "Can we reschedule our meeting to tomorrow at 10 AM?"
        JSON: {{"date": "2025-04-11", "time": "10:00", "title": "Meeting", "timeZone": "Asia/Kolkata"}}

        Example 3:
        Email: "The project deadline is next week."
        JSON: {{}}

        Example 4:
        Email: "I would want you postpone the scheduled timings of the meeting from 4 PM 10th April 2025 to 4PM 14th April 2025"
        JSON: {{"date": "2025-04-14", "time": "16:00", "title": "Meeting", "timeZone": "Asia/Kolkata"}}

        Email: "{email_body}"
        JSON:
        """
        response = model.generate_content(prompt)
        raw_output = response.text # store raw response
        print(f"Raw LLM Response: {raw_output}")
        # Clean the response
        cleaned_output = re.sub(r'```(?:json)?\s*', '', raw_output).strip() # clean the output
        # Return the cleaned JSON string directly instead of parsing it
        return cleaned_output
    except Exception as e:
        print(f"Error extracting meeting details: {e}")
        return "{}"