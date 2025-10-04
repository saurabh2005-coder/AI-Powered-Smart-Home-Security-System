# server/notification.py
# Simple Twilio SMS helper (optional)
from twilio.rest import Client
import os

TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "")

def send_sms(to, body):
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_FROM:
        print("Twilio not configured. Skipping SMS.")
        return
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    msg = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
    return msg.sid
