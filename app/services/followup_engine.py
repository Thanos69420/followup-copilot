from datetime import date


def days_overdue(due_date: date) -> int:
    return (date.today() - due_date).days


def risk_score(amount: float, due_date: date, last_contact_date: date | None) -> int:
    overdue = max(days_overdue(due_date), 0)
    amount_factor = min(int(amount / 250), 40)
    recency_penalty = 0 if last_contact_date else 10
    return min(overdue * 3 + amount_factor + recency_penalty, 100)


def urgency_from_risk(risk: int) -> str:
    if risk >= 75:
        return "high"
    if risk >= 40:
        return "medium"
    return "low"


def generate_draft(client_name: str, invoice_id: str, amount: float, due_date: date, last_contact_date: date | None):
    risk = risk_score(amount, due_date, last_contact_date)
    urg = urgency_from_risk(risk)
    overdue_days = max(days_overdue(due_date), 0)

    subject = f"Quick follow-up on invoice {invoice_id}"
    body = (
        f"Hi {client_name},\n\n"
        f"Quick follow-up on invoice {invoice_id} (${amount:,.2f}), currently {overdue_days} day(s) overdue. "
        "Could you share an expected payment date?\n\n"
        "Thanks — appreciate it."
    )
    if urg == "high":
        body += "\n\nIf useful, I can resend the invoice or split into milestones."

    return {
        "subject": subject,
        "body": body,
        "urgency": urg,
        "risk_score": risk,
    }
