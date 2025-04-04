from googleapiclient.discovery import build
import datetime
import json
import os
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/calendar']

# def create_calendar():
#     try:
#         credentials = service_account.Credentials.from_service_account_file(
#             os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
#             scopes=['https://www.googleapis.com/auth/calendar']
#         )
#         service = build('calendar', 'v3', credentials=credentials)
#         calendar_data = {
#             'summary': 'calendar-api-service-acc Calendar'
#         }
#         created_calendar = service.calendars().insert(body=calendar_data).execute()
#         print(f"Calendar created: {created_calendar['id']}")
#         return created_calendar['id']
#     except Exception as e:
#         print(f"Error creating calendar: {e}")
#         return None

def get_calendar_id():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        calendar_list = service.calendarList().list().execute()
        print("Full calendarList response:", calendar_list)
        print("Calendar list items:", calendar_list.get('items'))
        for calendar in calendar_list.get('items', []):
            print("Calendar summary:", calendar['summary'])
            if calendar['summary'] == 'calendar-api-service-acc Calendar': # Corrected comparison
                print("Found matching calendar ID:", calendar['id'])
                return calendar['id']
        print("No matching calendar found.")
        return None
    except Exception as e:
        print(f"Error getting calendar ID: {e}")
        return None
def schedule_event(calendar_id, event_details):
    """Schedules an event on the specified Google Calendar."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)

        # Accept a dictionary and convert it to JSON
        if isinstance(event_details, dict):
            event_details = json.dumps(event_details)

        try:
            event_data = json.loads(event_details)
            date_str = event_data.get("date")
            time_str = event_data.get("time")
            title = event_data.get("title", "Meeting")
            time_zone = event_data.get("timeZone", "UTC")
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            print(f"Error parsing event details JSON: {e}")
            return "Error: Invalid event details format."

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
            start_datetime = datetime.datetime.combine(date_obj, time_obj)
            end_datetime = start_datetime + datetime.timedelta(hours=1)
        except (ValueError, TypeError) as e:
            print(f"Error parsing date/time: {e}")
            return "Error: Invalid date or time format."

        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': time_zone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': time_zone,
            },
        }

        try:
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event creation successful. Response: {event}")
            return f'Event created: {event.get("htmlLink")}'
        except Exception as e:
            print(f"Error creating event in Google Calendar: {e}")
            print(f"Exception details: {e}")
            return f'Could not create event: {e}'

    except Exception as e:
        print(f"Error building calendar service: {e}")
        return f'Could not create event: {e}'


def share_calendar(calendar_id, user_email):
    try:
        service = build('calendar', 'v3', credentials=None)
        rule = {
            'scope': {
                'type': 'user',
                'value': user_email
            },
            'role': 'writer'
        }
        acl_response = service.acl().insert(calendarId=calendar_id, body=rule).execute()
        print("ACL insert response:", acl_response)  # Enhanced debug
        print(f"Calendar {calendar_id} shared with {user_email}")
    except Exception as e:
        print(f"Error sharing calendar: {e}")

if __name__ == '__main__':
    calendar_id = get_calendar_id()
    if not calendar_id:
        # You might want to uncomment the create_calendar function
        # calendar_id = create_calendar()
        print("Could not find calendar ID.")
    else:
        print(f"Calendar ID: {calendar_id}")
        
        # Share calendar with your personal email
        share_calendar(calendar_id, "guestacc.jan12000@gmail.com")
        
        # Schedule event on the SHARED calendar, not on 'primary'
        event_details_json = '{"title": "Test Meeting", "date": "2025-04-15", "time": "14:00", "timeZone": "UTC"}'
        print(schedule_event(calendar_id, event_details_json))
        
        print("\nIMPORTANT: Check your personal email for calendar sharing invitation and accept it!")