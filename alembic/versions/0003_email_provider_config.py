"""email provider config table

Revision ID: 0003_email_provider_config
Revises: 0002_send_events_and_approval
Create Date: 2026-03-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_email_provider_config"
down_revision = "0002_send_events_and_approval"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_provider_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="smtp"),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_uri", sa.String(length=255), nullable=True),
        sa.Column("client_id", sa.String(length=255), nullable=True),
        sa.Column("client_secret", sa.String(length=255), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("from_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_email_provider_org", "email_provider_configs", ["organization_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_email_provider_org", table_name="email_provider_configs")
    op.drop_table("email_provider_configs")
