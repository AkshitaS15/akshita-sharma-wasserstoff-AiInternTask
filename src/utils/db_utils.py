import sqlite3
import os

def store_email_in_db(email_data, db_path="email_data.db"):
    """
    Stores email data in an SQLite database, including a calendar_shared flag.
    If the table exists, it adds the calendar_shared column if it's missing.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
        table_exists = cursor.fetchone()

        if table_exists:
            # Table exists, check if calendar_shared column exists
            cursor.execute("PRAGMA table_info(emails)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'calendar_shared' not in columns:
                # Add the calendar_shared column
                cursor.execute("ALTER TABLE emails ADD COLUMN calendar_shared INTEGER DEFAULT 0")
                print("Added 'calendar_shared' column to the 'emails' table.")

        else:
            # Table doesn't exist, create it with calendar_shared column
            cursor.execute("""
                CREATE TABLE emails (
                    sender TEXT,
                    recipient TEXT,
                    subject TEXT,
                    timestamp TEXT,
                    body TEXT,
                    calendar_shared INTEGER DEFAULT 0
                )
            """)
            print("Created 'emails' table with 'calendar_shared' column.")

        cursor.execute("INSERT INTO emails VALUES (?, ?, ?, ?, ?, ?)", (
            email_data["sender"],
            email_data["recipient"],
            email_data["subject"],
            email_data["timestamp"],
            email_data["body"],
            0  # Initial calendar_shared value (0)
        ))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error storing in DB: {e}")