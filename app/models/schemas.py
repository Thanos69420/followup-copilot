from datetime import date
from pydantic import BaseModel, EmailStr


class Invoice(BaseModel):
    client_name: str
    client_email: EmailStr
    invoice_id: str
    amount: float
    due_date: date
    last_contact_date: date | None = None
    status: str = "sent"


class FollowupDraft(BaseModel):
    invoice_id: str
    client_email: EmailStr
    subject: str
    body: str
    urgency: str
    risk_score: int
