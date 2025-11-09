"""Document schemas"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DocumentBase(BaseModel):
    title: str
    orig_filename: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: UUID
    rel_path: str
    mime_type: str
    page_count: int
    status: str
    hash_sha256: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentPageResponse(BaseModel):
    id: UUID
    page_index: int
    ocr_text: Optional[str] = None
    preview_rel_path: Optional[str] = None
    thumb_rel_path: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentSummaryResponse(BaseModel):
    summary_md: Optional[str] = None
    keywords: Optional[List[str]] = None
    structured: Optional[dict] = None

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    pages: List[DocumentPageResponse] = []
    summary: Optional[DocumentSummaryResponse] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
