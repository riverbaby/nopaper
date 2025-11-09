"""Audit log models"""
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base, UUIDMixin, TimestampMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Audit log table"""

    __tablename__ = "audit_logs"

    actor = Column(String(200), nullable=False)
    action = Column(String(100), nullable=False)
    target_id = Column(String(200), nullable=True)
    meta = Column(JSONB, nullable=True)
