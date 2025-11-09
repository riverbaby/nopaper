"""Embedding services"""
from app.config import get_settings
from .base import EmbeddingService
from .local import LocalEmbeddingService

settings = get_settings()


def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance based on configuration"""
    if settings.EMBED_PROVIDER == "local_service":
        return LocalEmbeddingService()
    # Add other implementations here (openai_compatible, etc.)
    raise ValueError(f"Unsupported embedding provider: {settings.EMBED_PROVIDER}")


__all__ = ["EmbeddingService", "get_embedding_service"]
