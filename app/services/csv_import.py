import csv
from io import StringIO
from app.models.schemas import Invoice


def parse_invoice_csv(content: str) -> list[Invoice]:
    reader = csv.DictReader(StringIO(content))
    invoices: list[Invoice] = []
    for row in reader:
        invoices.append(
            Invoice(
                client_name=row["client_name"],
                client_email=row["client_email"],
                invoice_id=row["invoice_id"],
                amount=float(row["amount"]),
                due_date=row["due_date"],
                last_contact_date=row.get("last_contact_date") or None,
                status=row.get("status") or "sent",
            )
        )
    return invoices
