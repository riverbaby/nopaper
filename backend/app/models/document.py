"""Document models"""
import enum
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin, TimestampMixin


class DocumentStatus(str, enum.Enum):
    """Document processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Document(Base, UUIDMixin, TimestampMixin):
    """Document table"""

    __tablename__ = "documents"

    title = Column(String(500), nullable=False)
    orig_filename = Column(String(500), nullable=False)
    rel_path = Column(String(1000), nullable=False)
    mime_type = Column(String(100), nullable=False)
    page_count = Column(Integer, default=0)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    hash_sha256 = Column(String(64), nullable=False, index=True)
    error = Column(Text, nullable=True)

    # Relationships
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    summary = relationship("DocumentSummary", back_populates="document", uselist=False, cascade="all, delete-orphan")
    meta = relationship("DocumentMeta", back_populates="document", cascade="all, delete-orphan")
    tags = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")
    collections = relationship("DocumentCollection", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base, UUIDMixin):
    """Document page table"""

    __tablename__ = "document_pages"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_index = Column(Integer, nullable=False)
    ocr_text = Column(Text, nullable=True)
    preview_rel_path = Column(String(1000), nullable=True)
    thumb_rel_path = Column(String(1000), nullable=True)
    bbox_json = Column(JSONB, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="pages")


class DocumentSummary(Base, UUIDMixin):
    """Document summary table"""

    __tablename__ = "document_summaries"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary_md = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    structured = Column(JSONB, nullable=True)
    provider = Column(JSONB, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="summary")


class DocumentMeta(Base, UUIDMixin):
    """Document metadata table"""

    __tablename__ = "document_meta"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(JSONB, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="meta")
