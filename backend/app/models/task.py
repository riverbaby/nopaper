"""Task models"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin


class TaskStatus(str, enum.Enum):
    """Task status"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


class TaskStep(str, enum.Enum):
    """Task step"""

    OCR = "ocr"
    SUMMARIZE = "summarize"
    EMBED = "embed"
    THUMBNAIL = "thumbnail"
    PREVIEW = "preview"


class Task(Base, UUIDMixin):
    """Task table"""

    __tablename__ = "tasks"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    step = Column(SQLEnum(TaskStep), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    attempts = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    payload = Column(JSONB, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="tasks")
