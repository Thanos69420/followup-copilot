from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.db_models import InvoiceRecord, FollowupDraftRecord, SendEventRecord


def org_metrics(db: Session, organization_id: int) -> dict:
    total_invoices = db.execute(
        select(func.count()).select_from(InvoiceRecord).where(InvoiceRecord.organization_id == organization_id)
    ).scalar_one()

    overdue_open = db.execute(
        select(func.count()).select_from(InvoiceRecord).where(
            InvoiceRecord.organization_id == organization_id,
            InvoiceRecord.status.notin_(["paid", "void", "canceled"]),
        )
    ).scalar_one()

    total_drafts = db.execute(
        select(func.count()).select_from(FollowupDraftRecord).where(FollowupDraftRecord.organization_id == organization_id)
    ).scalar_one()

    approved_drafts = db.execute(
        select(func.count()).select_from(FollowupDraftRecord).where(
            FollowupDraftRecord.organization_id == organization_id,
            FollowupDraftRecord.approved.is_(True),
        )
    ).scalar_one()

    sent_events = db.execute(
        select(func.count()).select_from(SendEventRecord).where(
            SendEventRecord.organization_id == organization_id,
            SendEventRecord.outcome == "sent",
        )
    ).scalar_one()

    failed_events = db.execute(
        select(func.count()).select_from(SendEventRecord).where(
            SendEventRecord.organization_id == organization_id,
            SendEventRecord.outcome == "failed",
        )
    ).scalar_one()

    return {
        "total_invoices": int(total_invoices or 0),
        "open_invoices": int(overdue_open or 0),
        "total_drafts": int(total_drafts or 0),
        "approved_drafts": int(approved_drafts or 0),
        "send_success": int(sent_events or 0),
        "send_failed": int(failed_events or 0),
    }
