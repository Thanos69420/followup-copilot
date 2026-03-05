from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

from app.core.config import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def build_flow(state: str | None = None) -> Flow:
    if not settings.gmail_client_id or not settings.gmail_client_secret:
        raise ValueError("Gmail OAuth is not configured")

    client_config = {
        "web": {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.gmail_redirect_uri],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = settings.gmail_redirect_uri
    return flow


def auth_url(state: str) -> str:
    flow = build_flow(state=state)
    url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return url


def exchange_code(code: str):
    flow = build_flow()
    flow.fetch_token(code=code)
    c = flow.credentials
    return {
        "access_token": c.token,
        "refresh_token": c.refresh_token,
        "token_uri": c.token_uri,
        "client_id": c.client_id,
        "client_secret": c.client_secret,
        "scopes": c.scopes,
    }


def _build_credentials(access_token: str, refresh_token: str | None, token_uri: str, client_id: str, client_secret: str) -> Credentials:
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def gmail_profile(access_token: str, refresh_token: str | None, token_uri: str, client_id: str, client_secret: str):
    creds = _build_credentials(access_token, refresh_token, token_uri, client_id, client_secret)
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    return {
        "email": profile.get("emailAddress"),
        "access_token": creds.token,
    }


def send_gmail(access_token: str, refresh_token: str | None, token_uri: str, client_id: str, client_secret: str, to_email: str, subject: str, body: str):
    creds = _build_credentials(access_token, refresh_token, token_uri, client_id, client_secret)

    service = build("gmail", "v1", credentials=creds)
    msg = MIMEText(body)
    msg["to"] = to_email
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return {
        "sent": True,
        "provider": "gmail",
        "access_token": creds.token,
    }
