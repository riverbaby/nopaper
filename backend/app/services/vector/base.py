"""Base vector store interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VectorItem:
    """Vector item for upserting"""

    id: str
    vector: List[float]
    metadata: Dict[str, Any]


@dataclass
class ScoredItem:
    """Scored search result"""

    id: str
    score: float
    metadata: Dict[str, Any]


class VectorStore(ABC):
    """Abstract vector store interface"""

    @abstractmethod
    async def upsert(self, items: List[VectorItem]) -> None:
        """Upsert vector items"""
        pass

    @abstractmethod
    async def query(
        self, vector: List[float], k: int = 20, filter: Optional[Dict[str, Any]] = None
    ) -> List[ScoredItem]:
        """Query similar vectors"""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete vectors by IDs"""
        pass

    async def reindex(self) -> None:
        """Reindex (optional, for some implementations)"""
        pass

    async def ensure_collection(self) -> None:
        """Ensure collection/index exists"""
        pass
