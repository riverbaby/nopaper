"""Qdrant vector store implementation"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings
from .base import VectorStore, VectorItem, ScoredItem

settings = get_settings()


class QdrantVectorStore(VectorStore):
    """Qdrant vector store implementation"""

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION

    async def ensure_collection(self, dim: int = 1024) -> None:
        """Ensure collection exists"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    async def upsert(self, items: List[VectorItem]) -> None:
        """Upsert vector items"""
        if not items:
            return

        # Ensure collection exists with correct dimensions
        if items:
            await self.ensure_collection(dim=len(items[0].vector))

        points = [
            PointStruct(id=item.id, vector=item.vector, payload=item.metadata) for item in items
        ]

        self.client.upsert(collection_name=self.collection_name, points=points)

    async def query(
        self, vector: List[float], k: int = 20, filter: Optional[Dict[str, Any]] = None
    ) -> List[ScoredItem]:
        """Query similar vectors"""
        # Build Qdrant filter
        qdrant_filter = None
        if filter:
            conditions = []
            for key, value in filter.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            if conditions:
                qdrant_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=k,
            query_filter=qdrant_filter,
        )

        return [
            ScoredItem(id=str(result.id), score=result.score, metadata=result.payload or {})
            for result in results
        ]

    async def delete(self, ids: List[str]) -> None:
        """Delete vectors by IDs"""
        if not ids:
            return

        self.client.delete(collection_name=self.collection_name, points_selector=ids)
