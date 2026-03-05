from datetime import date
from sqlalchemy import select

from app.db import SessionLocal
from app.models.db_models import InvoiceRecord, FollowupDraftRecord
from app.services.followup_engine import days_overdue, generate_draft


ESCALATE_AT_DAYS = 14


def process_once() -> dict:
    db = SessionLocal()
    created = 0
    try:
        invoices = db.execute(select(InvoiceRecord).where(InvoiceRecord.status.notin_(["paid", "void", "canceled"]))).scalars().all()

        for inv in invoices:
            if days_overdue(inv.due_date) < ESCALATE_AT_DAYS:
                continue

            existing = db.execute(
                select(FollowupDraftRecord).where(
                    FollowupDraftRecord.organization_id == inv.organization_id,
                    FollowupDraftRecord.invoice_ref == inv.invoice_id,
                    FollowupDraftRecord.urgency == "high",
                    FollowupDraftRecord.status.in_(["draft", "queued", "retry", "sent"]),
                )
            ).scalar_one_or_none()
            if existing:
                continue

            d = generate_draft(inv.client_name, inv.invoice_id, inv.amount, inv.due_date, inv.last_contact_date)
            d["urgency"] = "high"
            rec = FollowupDraftRecord(
                organization_id=inv.organization_id,
                invoice_ref=inv.invoice_id,
                client_email=inv.client_email,
                subject="Final reminder: " + d["subject"],
                body=d["body"] + "\n\nThis is a final reminder before account hold.",
                urgency="high",
                risk_score=max(d["risk_score"], 85),
                status="draft",
                approved=False,
            )
            db.add(rec)
            created += 1

        db.commit()
        return {"escalations_created": created}
    finally:
        db.close()


if __name__ == "__main__":
    print(process_once())
