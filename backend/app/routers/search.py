"""Search and RAG routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from app.database import get_db
from app.models import Document, DocumentPage, Embedding
from app.schemas.search import SearchRequest, SearchResponse, SearchResult, ChatRequest, ChatResponse
from app.services.embed import get_embedding_service
from app.services.vector import get_vector_store
from app.services.llm import get_llm_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db = Depends(get_db),
):
    """Hybrid search: BM25 + Vector"""
    embed_service = get_embedding_service()
    vector_store = get_vector_store()

    results = []

    if request.hybrid:
        # Vector search
        query_vector = await embed_service.embed_text(request.q)
        vector_results = await vector_store.query(query_vector, k=request.k, filter=request.filters)

        # Get documents and pages
        for item in vector_results:
            doc_id = item.metadata.get("document_id")
            page_index = item.metadata.get("page_index")

            # Fetch document
            doc_result = await db.execute(select(Document).where(Document.id == doc_id))
            doc = doc_result.scalar_one_or_none()

            if doc:
                results.append(
                    SearchResult(
                        document_id=doc.id,
                        title=doc.title,
                        page_index=page_index,
                        score=item.score,
                        excerpt=item.metadata.get("text", ""),
                        metadata=item.metadata,
                    )
                )
    else:
        # Simple keyword search in document titles and OCR text
        query = (
            select(Document)
            .join(DocumentPage)
            .where(
                or_(
                    Document.title.ilike(f"%{request.q}%"),
                    DocumentPage.ocr_text.ilike(f"%{request.q}%"),
                )
            )
            .limit(request.k)
        )

        doc_result = await db.execute(query)
        docs = doc_result.scalars().all()

        for doc in docs:
            results.append(
                SearchResult(
                    document_id=doc.id,
                    title=doc.title,
                    score=1.0,
                    excerpt="",
                )
            )

    return SearchResponse(
        results=results,
        total=len(results),
        query=request.q,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db = Depends(get_db),
):
    """RAG chat endpoint"""
    embed_service = get_embedding_service()
    vector_store = get_vector_store()
    llm_service = get_llm_service()

    # Search for relevant chunks
    query_vector = await embed_service.embed_text(request.message)
    vector_results = await vector_store.query(query_vector, k=request.k, filter=request.filters)

    # Build context from search results
    context_parts = []
    citations = []

    for idx, item in enumerate(vector_results):
        doc_id = item.metadata.get("document_id")
        page_index = item.metadata.get("page_index")
        text = item.metadata.get("text", "")

        context_parts.append(f"[{idx+1}] {text}")

        # Fetch document for citation
        doc_result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = doc_result.scalar_one_or_none()

        if doc:
            citations.append(
                SearchResult(
                    document_id=doc.id,
                    title=doc.title,
                    page_index=page_index,
                    score=item.score,
                    excerpt=text,
                )
            )

    context = "\n\n".join(context_parts)

    # Generate response
    prompt = f"""基于以下文档内容回答用户的问题。请引用相关的文档编号。

文档内容：
{context}

用户问题：{request.message}

请提供详细的回答："""

    llm_response = await llm_service.generate(prompt)

    return ChatResponse(
        message=llm_response.text,
        citations=citations if request.with_citations else None,
    )
