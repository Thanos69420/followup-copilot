import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.models.db_models import EmailProviderConfig
from app.services.gmail_oauth import send_gmail


def send_email(to_email: str, subject: str, body: str, provider_cfg: EmailProviderConfig | None = None) -> dict:
    if provider_cfg and provider_cfg.provider == "gmail" and provider_cfg.access_token and provider_cfg.client_id and provider_cfg.client_secret and provider_cfg.token_uri:
        try:
            result = send_gmail(
                access_token=provider_cfg.access_token,
                refresh_token=provider_cfg.refresh_token,
                token_uri=provider_cfg.token_uri,
                client_id=provider_cfg.client_id,
                client_secret=provider_cfg.client_secret,
                to_email=to_email,
                subject=subject,
                body=body,
            )
            provider_cfg.access_token = result.get("access_token", provider_cfg.access_token)
            return {"sent": True, "provider": "gmail"}
        except Exception as e:
            return {"sent": False, "provider": "gmail", "reason": f"Gmail send failed: {e}"}

    if settings.smtp_host and settings.smtp_user and settings.smtp_pass:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.send_message(msg)

        return {"sent": True, "provider": "smtp"}

    return {
        "sent": False,
        "provider": "smtp",
        "reason": "No email provider configured (SMTP missing; Gmail API not configured)",
    }
