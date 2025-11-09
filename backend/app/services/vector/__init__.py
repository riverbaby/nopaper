"""Vector store services"""
from app.config import get_settings
from .base import VectorStore, VectorItem, ScoredItem
from .qdrant import QdrantVectorStore

settings = get_settings()


def get_vector_store() -> VectorStore:
    """Get vector store instance based on configuration"""
    if settings.VECTOR_BACKEND == "qdrant":
        return QdrantVectorStore()
    # Add other implementations here
    raise ValueError(f"Unsupported vector backend: {settings.VECTOR_BACKEND}")


__all__ = ["VectorStore", "VectorItem", "ScoredItem", "get_vector_store"]
