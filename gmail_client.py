import base64
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Draft creation is supported with gmail.compose.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError(
            "credentials.json was not found. Download your Google OAuth "
            "Desktop App credentials and place the file in this project folder."
        )

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def create_gmail_draft(to_email: str, subject: str, body: str) -> str:
    """
    Creates a Gmail draft only.
    This function never sends the message.
    """
    service = get_gmail_service()

    message = EmailMessage()
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    draft = (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={"message": {"raw": encoded_message}},
        )
        .execute()
    )

    return draft["id"]
