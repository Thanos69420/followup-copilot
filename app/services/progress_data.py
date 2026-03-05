from datetime import datetime, timezone


def current_progress():
    return {
        "project": "Followup Copilot",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "completion_percent": 64,
        "phases": [
            {"name": "Core API + Auth", "status": "done"},
            {"name": "Invoice + Draft Engine", "status": "done"},
            {"name": "Approval + Audit", "status": "done"},
            {"name": "Workers + Retry + Escalation", "status": "done"},
            {"name": "Gmail OAuth", "status": "in_progress"},
            {"name": "Accounting Sync", "status": "todo"},
            {"name": "Production Hardening", "status": "todo"},
        ],
        "changelog": [
            "Live deploy on Render (Docker)",
            "Added /ui dashboard for draft approval + send",
            "Added /events/send audit endpoint",
            "Added /status endpoint",
            "Added render.yaml + smoke checks",
            "Gmail connect/status scaffolding added",
        ],
        "next_5": [
            "Finish Gmail OAuth callback validation with real credentials",
            "Add team role permissions",
            "Add Stripe/QuickBooks connectors",
            "Add analytics widgets to /ui",
            "Add one-click demo dataset loader",
        ],
    }
