from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

SENDER = os.getenv("TWILIO_SEND_NUMBER")
RECEIVER = os.getenv("TWILIO_RECEIVE_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def send_notification(url=None, event="person_motion"):
    """Send a notification. If `url` is provided it will be included.
    `event` can be 'person_motion' or 'camera_moved' or other custom tags.
    """
    now = datetime.now()
    formatted_now = now.strftime("%d/%m/%y %H:%M:%S")

    if event == "camera_moved":
        if url:
            body = f"Camera movement detected @{formatted_now}: {url}"
        else:
            body = f"Camera movement detected @{formatted_now}."
    else:
        # default / person motion
        if url:
            body = f"Person motion detected @{formatted_now}: {url}"
        else:
            body = f"Person motion detected @{formatted_now}."

    client.messages.create(
        body=body,
        from_=SENDER,
        to=RECEIVER
    )