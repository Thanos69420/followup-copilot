from datetime import date
import csv
from io import StringIO
from pathlib import Path

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.db_models import (
    Organization,
    User,
    InvoiceRecord,
    FollowupDraftRecord,
    SendEventRecord,
    EmailProviderConfig,
)
from app.models.api_schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    SendDraftRequest,
    ApproveDraftRequest,
)
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings
from app.services.followup_engine import generate_draft, days_overdue
from app.services.email_sender import send_email
from app.services.gmail_oauth import auth_url, exchange_code, gmail_profile
from app.services.progress_data import current_progress

app = FastAPI(title="Followup Copilot", version="0.3.0")


@app.get("/ui")
def ui():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/progress")
def progress_ui():
    return FileResponse(Path(__file__).parent / "static" / "progress.html")


@app.get("/progress.json")
def progress_json():
    return current_progress()


def _get_current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/health")
def health():
    return {"ok": True, "version": "0.3.0", "service": "followup-copilot"}


@app.get("/status")
def status():
    return {
        "name": "followup-copilot",
        "api": "up",
        "ui": ["/ui", "/progress"],
        "features": {
            "auth": True,
            "invoice_import": True,
            "drafts": True,
            "approval": True,
            "send_audit": True,
            "gmail_oauth_scaffold": True,
            "workers": True,
        },
    }


@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == req.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(name=req.organization_name)
    db.add(org)
    db.flush()

    user = User(email=req.email, password_hash=hash_password(req.password), organization_id=org.id)
    db.add(user)
    db.commit()

    token = create_access_token(req.email)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == req.email)).scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(req.email)
    return TokenResponse(access_token=token)


@app.get("/auth/gmail/start")
def gmail_start(user: User = Depends(_get_current_user)):
    state = str(user.organization_id)
    try:
        url = auth_url(state=state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"auth_url": url, "redirect_uri": settings.gmail_redirect_uri}


@app.get("/auth/gmail/callback")
def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    # state carries organization_id
    try:
        org_id = int(state)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state")

    tokens = exchange_code(code)
    cfg = db.execute(select(EmailProviderConfig).where(EmailProviderConfig.organization_id == org_id)).scalar_one_or_none()
    if not cfg:
        cfg = EmailProviderConfig(organization_id=org_id)
        db.add(cfg)

    cfg.provider = "gmail"
    cfg.access_token = tokens.get("access_token")
    cfg.refresh_token = tokens.get("refresh_token") or cfg.refresh_token
    cfg.token_uri = tokens.get("token_uri")
    cfg.client_id = tokens.get("client_id")
    cfg.client_secret = tokens.get("client_secret")
    cfg.scope = " ".join(tokens.get("scopes") or [])

    try:
        prof = gmail_profile(
            access_token=cfg.access_token,
            refresh_token=cfg.refresh_token,
            token_uri=cfg.token_uri,
            client_id=cfg.client_id,
            client_secret=cfg.client_secret,
        )
        cfg.connected_email = prof.get("email")
        cfg.access_token = prof.get("access_token", cfg.access_token)
    except Exception:
        pass

    db.commit()
    return {"connected": True, "provider": "gmail", "organization_id": org_id, "email": cfg.connected_email}


@app.get("/auth/gmail/status")
def gmail_status(db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    cfg = db.execute(select(EmailProviderConfig).where(EmailProviderConfig.organization_id == user.organization_id)).scalar_one_or_none()
    if not cfg:
        return {"connected": False}
    return {
        "connected": cfg.provider == "gmail" and bool(cfg.access_token),
        "provider": cfg.provider,
        "scopes": cfg.scope,
        "email": cfg.connected_email,
    }


@app.post("/invoices/import")
async def import_invoices(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(_get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload CSV")

    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))

    imported = 0
    for row in reader:
        inv = InvoiceRecord(
            organization_id=user.organization_id,
            client_name=row["client_name"],
            client_email=row["client_email"],
            invoice_id=row["invoice_id"],
            amount=float(row["amount"]),
            due_date=date.fromisoformat(row["due_date"]),
            last_contact_date=date.fromisoformat(row["last_contact_date"]) if row.get("last_contact_date") else None,
            status=(row.get("status") or "sent").lower(),
        )
        db.add(inv)
        imported += 1

    db.commit()
    return {"imported": imported}


@app.get("/invoices")
def list_invoices(db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    invoices = db.execute(select(InvoiceRecord).where(InvoiceRecord.organization_id == user.organization_id)).scalars().all()
    return [
        {
            "client_name": i.client_name,
            "client_email": i.client_email,
            "invoice_id": i.invoice_id,
            "amount": i.amount,
            "due_date": i.due_date,
            "last_contact_date": i.last_contact_date,
            "status": i.status,
        }
        for i in invoices
    ]


@app.post("/followups/generate")
def build_followups(days: int = 3, db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    invoices = db.execute(select(InvoiceRecord).where(InvoiceRecord.organization_id == user.organization_id)).scalars().all()

    drafts = []
    for inv in invoices:
        if inv.status in {"paid", "void", "canceled"}:
            continue
        if days_overdue(inv.due_date) < days:
            continue

        d = generate_draft(
            client_name=inv.client_name,
            invoice_id=inv.invoice_id,
            amount=inv.amount,
            due_date=inv.due_date,
            last_contact_date=inv.last_contact_date,
        )
        rec = FollowupDraftRecord(
            organization_id=user.organization_id,
            invoice_ref=inv.invoice_id,
            client_email=inv.client_email,
            subject=d["subject"],
            body=d["body"],
            urgency=d["urgency"],
            risk_score=d["risk_score"],
            approved=False,
        )
        db.add(rec)
        drafts.append({"invoice_id": inv.invoice_id, **d, "client_email": inv.client_email, "approved": False})

    db.commit()
    return {"generated": len(drafts), "drafts": drafts}


@app.get("/followups")
def list_drafts(db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    rows = db.execute(select(FollowupDraftRecord).where(FollowupDraftRecord.organization_id == user.organization_id)).scalars().all()
    return [
        {
            "id": r.id,
            "invoice_id": r.invoice_ref,
            "client_email": r.client_email,
            "subject": r.subject,
            "body": r.body,
            "urgency": r.urgency,
            "risk_score": r.risk_score,
            "status": r.status,
            "approved": r.approved,
            "send_attempts": r.send_attempts,
            "last_error": r.last_error,
        }
        for r in rows
    ]


@app.post("/followups/approve")
def approve_draft(req: ApproveDraftRequest, db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    draft = db.execute(
        select(FollowupDraftRecord).where(
            FollowupDraftRecord.id == req.draft_id,
            FollowupDraftRecord.organization_id == user.organization_id,
        )
    ).scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    draft.approved = req.approved
    if req.approved and draft.status == "draft":
        draft.status = "queued"
    db.commit()
    return {"draft_id": draft.id, "approved": draft.approved, "status": draft.status}


@app.post("/followups/send")
def send_draft(req: SendDraftRequest, db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    draft = db.execute(
        select(FollowupDraftRecord).where(
            FollowupDraftRecord.id == req.draft_id,
            FollowupDraftRecord.organization_id == user.organization_id,
        )
    ).scalar_one_or_none()

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if not draft.approved:
        raise HTTPException(status_code=400, detail="Draft must be approved before send")

    provider_cfg = db.execute(
        select(EmailProviderConfig).where(EmailProviderConfig.organization_id == user.organization_id)
    ).scalar_one_or_none()

    result = send_email(draft.client_email, draft.subject, draft.body, provider_cfg=provider_cfg)
    draft.send_attempts += 1

    provider = result.get("provider", (provider_cfg.provider if provider_cfg else "smtp"))
    if result.get("sent"):
        draft.status = "sent"
        draft.last_error = None
        event = SendEventRecord(
            organization_id=user.organization_id,
            draft_id=draft.id,
            provider=provider,
            outcome="sent",
            error=None,
        )
    else:
        draft.status = "retry"
        draft.last_error = result.get("reason", "unknown error")
        event = SendEventRecord(
            organization_id=user.organization_id,
            draft_id=draft.id,
            provider=provider,
            outcome="failed",
            error=draft.last_error,
        )

    db.add(event)
    db.commit()

    return {"draft_id": draft.id, **result}


@app.get("/events/send")
def list_send_events(limit: int = 100, db: Session = Depends(get_db), user: User = Depends(_get_current_user)):
    rows = db.execute(
        select(SendEventRecord)
        .where(SendEventRecord.organization_id == user.organization_id)
        .order_by(SendEventRecord.id.desc())
        .limit(limit)
    ).scalars().all()

    return [
        {
            "id": r.id,
            "draft_id": r.draft_id,
            "provider": r.provider,
            "outcome": r.outcome,
            "error": r.error,
            "created_at": r.created_at,
        }
        for r in rows
    ]
