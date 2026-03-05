# Opportunity Research + Strategy

## Step 1 — 5 Opportunities

### 1) **Invoice Follow-Up Copilot for Freelancers/Small Agencies**
- **Problem:** Getting paid late and manually chasing clients via awkward reminders.
- **Who feels it:** Freelancers, boutique dev/design agencies, solo consultants.
- **Why existing tools fail:** Accounting tools send generic reminders, but not context-aware tone, escalation, or workflow automation.
- **Validation signals:**
  - Large volume of discussions about late payments in freelancer communities.
  - Cash-flow management repeatedly cited as a top SMB challenge.
  - Users currently patch this with spreadsheets + manual email drafting.
- **Monetization potential:** $29–$199/mo; viable path to $3k–$40k MRR with 100–400 customers.

### 2) **PR Review Bottleneck Agent (Engineering Teams)**
- **Problem:** Pull requests stall waiting for review; cycle time drifts.
- **Who feels it:** Eng managers, startups shipping fast.
- **Why existing tools fail:** Dashboards show metrics, but few agents actively unblock (smart nudges, reviewer assignment, summary generation).
- **Validation signals:** Team complaints around review latency are common; DORA/cycle-time focus remains high.
- **Monetization potential:** $99–$999/mo team pricing.

### 3) **Creator Sponsorship Inbox Triage + Negotiation Assistant**
- **Problem:** Creators lose deals by slow replies and poor pipeline tracking.
- **Who feels it:** Mid-tier YouTubers/TikTokers/newsletter creators.
- **Why existing tools fail:** CRM tools are overkill; inboxes are chaotic; negotiation scripting remains manual.
- **Validation signals:** Creator forums discuss sponsor outreach and missed follow-up constantly.
- **Monetization potential:** $49–$299/mo.

### 4) **ADHD Admin Load Automator (paperwork + scheduling + reminders)**
- **Problem:** Repetitive admin tasks cause paralysis and missed deadlines.
- **Who feels it:** ADHD professionals/students.
- **Why existing tools fail:** Task apps track tasks but don’t execute task fragments automatically.
- **Validation signals:** Significant demand for “done-for-you” executive-function support.
- **Monetization potential:** B2C $12–$49/mo, plus concierge tier.

### 5) **Local Business Missed-Call Recovery Agent**
- **Problem:** Missed calls = missed revenue.
- **Who feels it:** Dentists, clinics, plumbers, legal intake teams.
- **Why existing tools fail:** Basic voicemail transcription lacks conversion-focused follow-up workflows.
- **Validation signals:** Known speed-to-lead and missed-call leakage in local services.
- **Monetization potential:** $79–$499/location/mo.

---

## Step 2 — Selection

### Chosen: **Invoice Follow-Up Copilot**

**Why this wins now:**
1. **Solvable with AI agents:** Strong fit for drafting, sentiment/tone adjustment, escalation sequencing, payment-risk scoring.
2. **Monetization:** Clear pain with direct ROI (faster collection).
3. **Novel angle:** “Relationship-safe collections” with context-aware language and automated escalation, not just timer-based reminders.
4. **Speed to MVP:** Very fast. CSV import + risk scoring + draft generation works in days.

---

## Step 3 — Product Design

- **Product name:** Followup Copilot
- **Core concept:** AI assistant that decides *who to nudge, when, and how* so users get paid faster without burning client relationships.

### User workflow
1. Connect or import invoices.
2. System identifies overdue/risky invoices.
3. AI drafts personalized follow-ups by urgency tier.
4. User approves or auto-sends.
5. Product tracks responses and escalates only when needed.

### Key features
- Overdue detection + risk scoring
- Tone-aware email drafts
- Escalation playbooks (gentle → firm)
- Payment status sync (Stripe/QuickBooks)
- Daily action queue (“Send these 5 nudges”)

### MVP
- CSV import
- Risk scoring engine
- Follow-up draft generator API
- Automation-ready endpoints

### Defensibility
- Proprietary payment follow-up dataset (anonymized outcomes)
- Feedback loop on message effectiveness by segment
- Workflow integrations with accounting + email + CRM systems

---

## Step 4 — Technical Architecture

### Backend
- FastAPI service
- Modular services: ingestion, scoring, drafting, orchestration

### AI usage
- Prompt templates for tone + escalation
- Optional LLM for personalization (fallback deterministic templates)

### Data storage
- MVP: JSON file store
- Next: Postgres (invoices, reminders, outcomes, customer settings)

### APIs
- `/invoices/import`
- `/invoices`
- `/followups/generate`

### Automation flows
- n8n/Make/Zapier: trigger on overdue invoices
- Daily digest + auto-send queue

### Scaling
- Move to async job queue (Celery/Redis)
- Add multi-tenant auth + tenant isolation
- Cache scoring results + batched LLM calls

---

## Step 5 — Implementation Plan

### Phase 1 — Prototype (now)
- [x] Define problem and market angle
- [x] Create backend skeleton
- [x] Build CSV ingestion
- [x] Build scoring and draft generation
- [x] Write docs

### Phase 2 — MVP
- [ ] Add persistent DB (Postgres)
- [ ] Add auth + organizations
- [ ] Add Gmail/SMTP sender
- [ ] Add Stripe/QuickBooks sync
- [ ] Add approval UI (web)

### Phase 3 — Revenue-ready
- [ ] Outcome analytics dashboard
- [ ] A/B testing for follow-up copy
- [ ] Billing + subscription management
- [ ] Partner/referral channel program

Dependencies: email integration depends on auth and tenant settings; analytics depends on send/outcome events.

---

## Step 6 — Monetization Strategy

### Pricing
- Solo: $29/mo (up to 50 active invoices)
- Pro: $79/mo (up to 300)
- Agency: $199/mo (multi-client + white-label exports)
- Optional success fee add-on: % of recovered overdue amount beyond baseline

### Target customer
- Freelancers earning $3k–$40k monthly
- 2–20 person agencies
- Fractional operators handling many invoices

### Distribution
- Content: “collections without being a jerk” SEO + socials
- Integrations: QuickBooks, Xero, Stripe marketplaces
- Partnerships: bookkeeping firms and freelance communities

### First 100 customers plan
1. 20 design partners from freelancer communities
2. Offer free “overdue audit” import tool
3. Publish case studies showing days-sales-outstanding reduction
4. Launch referral incentive (1 free month per referral)
