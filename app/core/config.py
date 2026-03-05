from pydantic import BaseModel
import os


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./followup.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algo: str = "HS256"
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "1440"))

    smtp_host: str | None = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_pass: str | None = os.getenv("SMTP_PASS")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@followupcopilot.local")

    gmail_client_id: str | None = os.getenv("GMAIL_CLIENT_ID")
    gmail_client_secret: str | None = os.getenv("GMAIL_CLIENT_SECRET")
    gmail_redirect_uri: str = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8080/auth/gmail/callback")


settings = Settings()
