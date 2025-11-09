"""Local embedding implementation using sentence-transformers"""
import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from .base import EmbeddingService

settings = get_settings()


class LocalEmbeddingService(EmbeddingService):
    """Local embedding service using sentence-transformers"""

    def __init__(self):
        self.model = SentenceTransformer(settings.EMBED_MODEL)
        self.normalize = settings.EMBED_NORMALIZE

    async def embed_text(self, text: str) -> List[float]:
        """Embed single text"""
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, self._embed_sync, text)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of texts"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self._embed_batch_sync, texts)
        return [emb.tolist() for emb in embeddings]

    def _embed_sync(self, text: str):
        """Synchronous embedding"""
        return self.model.encode(text, normalize_embeddings=self.normalize)

    def _embed_batch_sync(self, texts: List[str]):
        """Synchronous batch embedding"""
        return self.model.encode(texts, normalize_embeddings=self.normalize)

    def get_dim(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()
