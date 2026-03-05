# API (v0.3)

## UI
- `GET /ui` lightweight approval UI (token entered manually)
- `GET /progress` visual sprint progress board

## Gmail OAuth
- `GET /auth/gmail/start` (bearer auth required; returns connect URL)
- `GET /auth/gmail/callback?code=...&state=...` (stores org provider tokens)
- `GET /auth/gmail/status` (bearer auth required)

After callback, provider tokens are persisted per organization and used for send attempts.

## Auth
### POST /auth/register
```json
{
  "organization_name": "Acme Studio",
  "email": "owner@acme.com",
  "password": "strongpass"
}
```
Response: `{ "access_token": "...", "token_type": "bearer" }`

### POST /auth/login
```json
{
  "email": "owner@acme.com",
  "password": "strongpass"
}
```

## Invoices
### POST /invoices/import
Multipart CSV upload. Requires `Authorization: Bearer <token>`.

### GET /invoices
Lists invoices for current organization.

## Followups
### POST /followups/generate?days=3
Generates and stores follow-up drafts for overdue invoices (default unapproved).

### GET /followups
Lists generated drafts.

### POST /followups/approve
```json
{ "draft_id": 1, "approved": true }
```

### POST /followups/send
```json
{ "draft_id": 1 }
```
Requires approved draft.

## Send Events
### GET /events/send?limit=50
Returns send audit events (provider, outcome, error, timestamp).

## Health
### GET /health
Returns service status/version.
