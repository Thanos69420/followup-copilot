# Followup Copilot (MVP)

AI-assisted invoice follow-up automation for freelancers and small agencies.

## Why this exists
Late payments kill cash flow. Existing invoice reminders are either too generic, too rigid, or disconnected from real client conversation context.

## MVP features
- Multi-tenant org + user auth (JWT)
- Import invoices (CSV) into DB
- Compute risk score + follow-up urgency
- Generate and persist follow-up drafts
- Send approved drafts over SMTP
- Expose API endpoints for automation workflows (Zapier/Make/n8n)

## Quickstart (local)
```bash
cd startup-lab/followup-copilot
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8080
```

## Quickstart (Docker)
```bash
cd startup-lab/followup-copilot
cp .env.example .env
docker compose up --build -d
# apply migrations inside api container
docker compose exec api alembic upgrade head
```

## Example CSV
```csv
client_name,client_email,invoice_id,amount,due_date,last_contact_date,status
Acme LLC,billing@acme.com,INV-001,1200,2026-03-01,2026-02-27,sent
```

## API
- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `POST /invoices/import` (multipart CSV, bearer auth)
- `GET /invoices`
- `POST /followups/generate?days=3`
- `GET /followups`
- `POST /followups/approve`
- `POST /followups/send`
- `GET /events/send`
- `GET /ui` (light approval UI)
- `GET /progress` (visual sprint board)
- `GET /auth/gmail/start` (returns OAuth URL)
- `GET /auth/gmail/status`

## Worker jobs
- `python -m app.workers.retry_worker` → one-shot send/retry pass
- `python -m app.workers.escalation_worker` → one-shot escalation pass
- `python -m scripts.worker_loop` → continuous worker loop (60s tick)

## Next integrations
- Gmail OAuth send + thread tracking
- Stripe/QuickBooks payment-status sync
- Slack daily “who needs a nudge” digest
