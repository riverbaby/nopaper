"""Document management routes"""
from typing import List, Optional
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDetailResponse
from app.config import get_settings
from app.utils.hash import sha256_file
from app.utils.fs import ensure_dir
from app.workers.tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


@router.post("/", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db = Depends(get_db),
):
    """Upload one or more documents"""
    results = []

    for file in files:
        # Save file
        file_path = Path(settings.DOCS_ROOT) / file.filename
        ensure_dir(file_path.parent)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Calculate hash
        file_hash = sha256_file(file_path)

        # Check for duplicates
        result = await db.execute(select(Document).where(Document.hash_sha256 == file_hash))
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # File already exists
            results.append(existing_doc)
            file_path.unlink()  # Delete duplicate
            continue

        # Create document record
        rel_path = str(file_path.relative_to(settings.DOCS_ROOT))
        document = Document(
            title=file.filename,
            orig_filename=file.filename,
            rel_path=rel_path,
            mime_type=file.content_type or "application/octet-stream",
            hash_sha256=file_hash,
            status=DocumentStatus.PENDING,
        )
        db.add(document)
        await db.flush()
        await db.refresh(document)

        # Queue processing task
        process_document_task.delay(str(document.id))

        results.append(document)

    await db.commit()
    return results


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db = Depends(get_db),
):
    """List documents with pagination"""
    query = select(Document).order_by(Document.created_at.desc())

    if status:
        query = query.where(Document.status == status)

    # Count total
    count_query = select(func.count()).select_from(Document)
    if status:
        count_query = count_query.where(Document.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=documents,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    db = Depends(get_db),
):
    """Get document details"""
    query = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.pages), selectinload(Document.summary))
    )

    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    db = Depends(get_db),
):
    """Delete a document"""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    file_path = Path(settings.DOCS_ROOT) / document.rel_path
    if file_path.exists():
        file_path.unlink()

    # Delete from database (cascade will handle related records)
    await db.delete(document)
    await db.commit()

    return {"status": "deleted", "document_id": str(document_id)}
