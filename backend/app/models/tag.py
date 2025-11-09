"""Tag and collection models"""
import enum
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin, TimestampMixin


class TagType(str, enum.Enum):
    """Tag type"""

    USER = "user"
    AUTO = "auto"
    OCR = "ocr"
    LLM = "llm"


class Tag(Base, UUIDMixin, TimestampMixin):
    """Tag table"""

    __tablename__ = "tags"

    name = Column(String(100), nullable=False, unique=True)
    type = Column(SQLEnum(TagType), default=TagType.USER, nullable=False)

    # Relationships
    documents = relationship("DocumentTag", back_populates="tag", cascade="all, delete-orphan")


class DocumentTag(Base, UUIDMixin):
    """Document-Tag association table"""

    __tablename__ = "document_tags"
    __table_args__ = (UniqueConstraint("document_id", "tag_id", name="uq_document_tag"),)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="documents")


class Collection(Base, UUIDMixin, TimestampMixin):
    """Collection table"""

    __tablename__ = "collections"

    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    documents = relationship("DocumentCollection", back_populates="collection", cascade="all, delete-orphan")


class DocumentCollection(Base, UUIDMixin):
    """Document-Collection association table"""

    __tablename__ = "document_collections"
    __table_args__ = (UniqueConstraint("document_id", "collection_id", name="uq_document_collection"),)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="collections")
    collection = relationship("Collection", back_populates="documents")
