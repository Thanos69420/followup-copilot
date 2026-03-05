"""send events + approval flag

Revision ID: 0002_send_events_and_approval
Revises: 0001_init
Create Date: 2026-03-03
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_send_events_and_approval"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("followup_drafts", sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "send_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("draft_id", sa.Integer(), sa.ForeignKey("followup_drafts.id"), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="smtp"),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_send_events_org", "send_events", ["organization_id"], unique=False)
    op.create_index("ix_send_events_draft", "send_events", ["draft_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_send_events_draft", table_name="send_events")
    op.drop_index("ix_send_events_org", table_name="send_events")
    op.drop_table("send_events")
    op.drop_column("followup_drafts", "approved")
