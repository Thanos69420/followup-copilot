# Net Build Sprint Log

## Sprint Goal
Move from prototype to MVP core with multi-tenant data model, authentication, and real outbound message path.

## Completed in this sprint
- Added SQLAlchemy data layer (SQLite default, Postgres-ready via `DATABASE_URL`)
- Added org/user/invoice/followup relational models
- Added JWT auth (`/auth/register`, `/auth/login`)
- Added tenant-scoped API access via bearer token dependency
- Added invoice CSV import into DB
- Added follow-up generation persisted to `followup_drafts`
- Added draft listing and send endpoint (`/followups/send`)
- Added SMTP sender service with graceful non-configured fallback
- Added environment template and updated dependencies

## Completed in sprint slice 2
- Added Alembic scaffolding + initial migration (`0001_init`)
- Added retry worker with exponential backoff schedule
- Added escalation worker for long-overdue invoices
- Added continuous worker loop runner
- Added Dockerfile + docker-compose (api + worker + postgres)
- Added runbook notes to README

## Completed in sprint slice 3
- Added send event audit table + migration (`0002_send_events_and_approval`)
- Added approval gate for drafts before sending
- Added `/events/send` audit endpoint
- Added lightweight approval UI at `/ui`
- Updated retry worker to process approved queued/retry drafts only

## Completed in sprint slice 4
- Added Gmail OAuth endpoints + provider config persistence
- Added Gmail profile capture (`connected_email`) post-connect
- Added UI buttons for Gmail connect/status in `/ui`
- Added token-refresh-capable Gmail send helper

## Deferred to next sprint
- End-to-end Gmail callback validation on live creds
- Stripe/QuickBooks sync connectors
- Role-based access controls for teams
