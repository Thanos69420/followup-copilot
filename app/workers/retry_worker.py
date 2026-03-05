from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.db import SessionLocal
from app.models.db_models import FollowupDraftRecord, SendEventRecord, EmailProviderConfig
from app.services.email_sender import send_email

MAX_ATTEMPTS = 5


def _next_retry_delay_minutes(attempt: int) -> int:
    schedule = [5, 15, 60, 180, 720]
    idx = min(attempt - 1, len(schedule) - 1)
    return schedule[idx]


def process_once() -> dict:
    now = datetime.now(timezone.utc)
    db = SessionLocal()
    sent = 0
    failed = 0

    try:
        q = select(FollowupDraftRecord).where(
            FollowupDraftRecord.approved.is_(True),
            FollowupDraftRecord.status.in_(["queued", "retry"]),
        )
        rows = db.execute(q).scalars().all()

        for draft in rows:
            if draft.next_retry_at and draft.next_retry_at > now:
                continue
            if draft.send_attempts >= MAX_ATTEMPTS:
                draft.status = "failed"
                continue

            provider_cfg = db.execute(
                select(EmailProviderConfig).where(EmailProviderConfig.organization_id == draft.organization_id)
            ).scalar_one_or_none()

            result = send_email(draft.client_email, draft.subject, draft.body, provider_cfg=provider_cfg)
            draft.send_attempts += 1
            provider = result.get("provider", (provider_cfg.provider if provider_cfg else "smtp"))

            if result.get("sent"):
                draft.status = "sent"
                draft.last_error = None
                draft.next_retry_at = None
                db.add(SendEventRecord(
                    organization_id=draft.organization_id,
                    draft_id=draft.id,
                    provider=provider,
                    outcome="sent",
                    error=None,
                ))
                sent += 1
            else:
                delay = _next_retry_delay_minutes(draft.send_attempts)
                draft.status = "retry"
                draft.last_error = result.get("reason", "unknown error")
                draft.next_retry_at = now + timedelta(minutes=delay)
                db.add(SendEventRecord(
                    organization_id=draft.organization_id,
                    draft_id=draft.id,
                    provider=provider,
                    outcome="failed",
                    error=draft.last_error,
                ))
                failed += 1

        db.commit()
        return {"sent": sent, "failed": failed}
    finally:
        db.close()


if __name__ == "__main__":
    print(process_once())
