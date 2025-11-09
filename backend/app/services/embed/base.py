"""Base embedding interface"""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingService(ABC):
    """Abstract embedding service interface"""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed single text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of texts"""
        pass

    @abstractmethod
    def get_dim(self) -> int:
        """Get embedding dimension"""
        pass
