"""add connected_email to email provider config

Revision ID: 0004_connected_email
Revises: 0003_email_provider_config
Create Date: 2026-03-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_connected_email"
down_revision = "0003_email_provider_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("email_provider_configs", sa.Column("connected_email", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("email_provider_configs", "connected_email")
