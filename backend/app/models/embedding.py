"""Embedding models"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin


class Embedding(Base, UUIDMixin):
    """Embedding table - stores metadata about embeddings, actual vectors in vector store"""

    __tablename__ = "embeddings"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_index = Column(Integer, nullable=True)
    chunk_id = Column(String(100), nullable=False)
    embedding_key = Column(String(200), nullable=False, unique=True)
    dim = Column(Integer, nullable=False)
    provider = Column(JSONB, nullable=True)
    text_excerpt = Column(Text, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="embeddings")
