"""Search schemas"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class SearchRequest(BaseModel):
    q: str
    filters: Optional[dict] = None
    k: int = 20
    hybrid: bool = True
    weights: Optional[dict] = None  # {"bm25": 0.4, "vec": 0.6}


class SearchResult(BaseModel):
    document_id: UUID
    title: str
    page_index: Optional[int] = None
    score: float
    excerpt: str
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


class ChatRequest(BaseModel):
    message: str
    filters: Optional[dict] = None
    k: int = 5
    with_citations: bool = True


class ChatResponse(BaseModel):
    message: str
    citations: Optional[List[SearchResult]] = None
