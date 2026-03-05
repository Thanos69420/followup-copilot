from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization")


class InvoiceRecord(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    invoice_id = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    last_contact_date = Column(Date, nullable=True)
    status = Column(String(50), default="sent", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FollowupDraftRecord(Base):
    __tablename__ = "followup_drafts"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    invoice_ref = Column(String(100), nullable=False, index=True)
    client_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    urgency = Column(String(20), nullable=False)
    risk_score = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    approved = Column(Boolean, nullable=False, default=False)
    send_attempts = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SendEventRecord(Base):
    __tablename__ = "send_events"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    draft_id = Column(Integer, ForeignKey("followup_drafts.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="smtp")
    outcome = Column(String(20), nullable=False)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailProviderConfig(Base):
    __tablename__ = "email_provider_configs"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True, unique=True)
    provider = Column(String(50), nullable=False, default="smtp")
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_uri = Column(String(255), nullable=True)
    client_id = Column(String(255), nullable=True)
    client_secret = Column(String(255), nullable=True)
    scope = Column(Text, nullable=True)
    from_email = Column(String(255), nullable=True)
    connected_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
