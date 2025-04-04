# src/models/email_model.py
from dataclasses import dataclass

@dataclass
class Email:
    sender: str
    recipient: str
    subject: str
    timestamp: str
    body: str