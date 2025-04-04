# Email Assistant Project README

This project aims to create an email assistant that automates various email-related tasks, including summarizing emails, inferring intent, drafting replies, extracting meeting details, scheduling calendar events, and sending Slack notifications for urgent emails.

## Project Overview

The assistant processes emails fetched from a Gmail account, utilizes a Large Language Model (LLM) for natural language processing tasks, interacts with Google Calendar for scheduling, and sends Slack notifications. It also stores email data in an SQLite database.

## Key Features

* **Email Fetching:**
    * Fetches emails from a Gmail account using IMAP.
* **Email Summarization:**
    * Summarizes email content using an LLM.
* **Intent Inference:**
    * Determines the intent of an email using an LLM.
* **Reply Drafting:**
    * Generates polite and concise replies using an LLM.
    * Saves reply as a draft in gmail.
* **Meeting Detail Extraction:**
    * Extracts meeting details (date, time, title, timezone) from emails using an LLM.
    * Handles rescheduling requests.
* **Calendar Scheduling:**
    * Schedules events on Google Calendar based on extracted meeting details.
    * Shares Calendar with given email, once per email sender.
* **Slack Notifications:**
    * Sends Slack notifications for emails marked as urgent.
* **Database Storage:**
    * Stores email data in an SQLite database.
    * Stores a flag to keep track of calendar sharing.
* **Web Search:**
    * Performs web searches from email body, using a web search service.

## Project Structure
Markdown

# Email Assistant Project README

This project aims to create an email assistant that automates various email-related tasks, including summarizing emails, inferring intent, drafting replies, extracting meeting details, scheduling calendar events, and sending Slack notifications for urgent emails.

## Project Overview

The assistant processes emails fetched from a Gmail account, utilizes a Large Language Model (LLM) for natural language processing tasks, interacts with Google Calendar for scheduling, and sends Slack notifications. It also stores email data in an SQLite database.

## Key Features

* **Email Fetching:**
    * Fetches emails from a Gmail account using IMAP.
* **Email Summarization:**
    * Summarizes email content using an LLM.
* **Intent Inference:**
    * Determines the intent of an email using an LLM.
* **Reply Drafting:**
    * Generates polite and concise replies using an LLM.
    * Saves reply as a draft in gmail.
* **Meeting Detail Extraction:**
    * Extracts meeting details (date, time, title, timezone) from emails using an LLM.
    * Handles rescheduling requests.
* **Calendar Scheduling:**
    * Schedules events on Google Calendar based on extracted meeting details.
    * Shares Calendar with given email, once per email sender.
* **Slack Notifications:**
    * Sends Slack notifications for emails marked as urgent.
* **Database Storage:**
    * Stores email data in an SQLite database.
    * Stores a flag to keep track of calendar sharing.
* **Web Search:**
    * Performs web searches from email body, using a web search service.

## Project Structure

Email_Assistant/
├── src/
│   ├── services/
│   │   ├── email_service.py
│   │   ├── llm_service.py
│   │   ├── web_search_service.py
│   │   ├── slack_service.py
│   │   ├── calendar_service.py
│   ├── controllers/
│   │   ├── main_controller.py
│   ├── utils/
│   │   ├── db_utils.py
│   ├── config.py
├── email_data.db
├── requirements.txt
└── README.md

* **`src/services/`:** Contains modules for interacting with external services (Gmail, LLM, Google Calendar, Slack, web search).
* **`src/controllers/`:** Contains the main application logic (`main_controller.py`).
* **`src/utils/`:** Contains utility functions, such as database interaction (`db_utils.py`).
* **`src/config.py`:** Stores configuration variables (API keys, credentials, etc.).
* **`email_data.db`:** The SQLite database file.
* **`requirements.txt`:** Lists the project's dependencies.
* **`README.md`:** This file.

## Key Implementation Details

* **LLM Integration:**
    * Utilizes the Google Gemini API for natural language processing tasks.
    * Prompts are carefully crafted to ensure accurate extraction of meeting details, even from rescheduling requests.
    * LLM output is cleaned to remove extra characters before JSON parsing.
* **Calendar Integration:**
    * Uses the Google Calendar API to schedule events.
    * Manages calendar sharing to prevent repeated invitations.
    * Accepts python dictionary, and converts it to json string before sending to google calendar API.
* **Database Management:**
    * Stores email data and calendar sharing flags in an SQLite database.
    * Implements robust database interaction with error handling.
* **Error Handling:**
    * Includes comprehensive error handling for database operations, API calls, and JSON parsing.
    * Provides informative error messages for debugging.
* **Path Management:**
    * Dynamically adds the project's root directory to `sys.path` to ensure correct module imports.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [repository URL]
    cd Email_Assistant
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    * **Windows:** `venv\Scripts\activate`
    * **macOS/Linux:** `source venv/bin/activate`
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure environment variables:**
    * Create a `src/config.py` file and add your API keys, email credentials, and Slack token.
    * Ensure that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set to the path of your Google Calendar API credentials file.
6.  **Run the application:**
    ```bash
    python src/controllers/main_controller.py
    ```

## Future Improvements

* **More sophisticated intent recognition.**
* **Allow user to modify reply before sending.**
* **Add support for more calendar features (e.g., reminders, recurring events).**
* **Improve error handling and logging.**
* **Add unit tests.**
* **Implement a user interface.**
* **Add more robust web search based on email context.**