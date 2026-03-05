from datetime import date
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class InvoiceOut(BaseModel):
    client_name: str
    client_email: EmailStr
    invoice_id: str
    amount: float
    due_date: date
    last_contact_date: date | None = None
    status: str


class FollowupDraftOut(BaseModel):
    invoice_id: str
    client_email: EmailStr
    subject: str
    body: str
    urgency: str
    risk_score: int


class SendDraftRequest(BaseModel):
    draft_id: int


class ApproveDraftRequest(BaseModel):
    draft_id: int
    approved: bool = True
