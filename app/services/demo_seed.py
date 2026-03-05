from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.db_models import InvoiceRecord


def seed_demo_invoices(db: Session, organization_id: int) -> int:
    today = date.today()
    rows = [
        ("Acme LLC", "billing@acme.com", "INV-DEMO-001", 1200.0, today - timedelta(days=18), today - timedelta(days=10), "sent"),
        ("Northwind Co", "ap@northwind.com", "INV-DEMO-002", 4500.0, today - timedelta(days=35), today - timedelta(days=20), "sent"),
        ("Bluebird Studio", "ops@bluebird.studio", "INV-DEMO-003", 300.0, today - timedelta(days=2), today - timedelta(days=2), "sent"),
        ("Paid Client", "payments@paid.com", "INV-DEMO-004", 800.0, today - timedelta(days=25), today - timedelta(days=22), "paid"),
    ]

    created = 0
    for client_name, client_email, invoice_id, amount, due, last_contact, status in rows:
        exists = db.query(InvoiceRecord).filter(
            InvoiceRecord.organization_id == organization_id,
            InvoiceRecord.invoice_id == invoice_id,
        ).first()
        if exists:
            continue

        db.add(InvoiceRecord(
            organization_id=organization_id,
            client_name=client_name,
            client_email=client_email,
            invoice_id=invoice_id,
            amount=amount,
            due_date=due,
            last_contact_date=last_contact,
            status=status,
        ))
        created += 1

    db.commit()
    return created
