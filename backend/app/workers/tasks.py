"""Celery tasks for document processing"""
import asyncio
from datetime import datetime
from pathlib import Path
from uuid import UUID
from celery import Task
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.models import Document, DocumentPage, DocumentSummary, Embedding, Task as TaskModel, TaskStatus, TaskStep, DocumentStatus
from app.database import AsyncSessionLocal
from app.services.pipeline import DocumentPipeline
from app.config import get_settings

settings = get_settings()


class DatabaseTask(Task):
    """Base task with database session"""

    _pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = DocumentPipeline()
        return self._pipeline


@celery_app.task(base=DatabaseTask, bind=True)
def process_document_task(self, document_id: str):
    """Process document through the pipeline"""
    return asyncio.run(_process_document_async(self, document_id))


async def _process_document_async(task_instance, document_id: str):
    """Async document processing"""
    doc_id = UUID(document_id)

    async with AsyncSessionLocal() as session:
        try:
            # Get document
            result = await session.execute(select(Document).where(Document.id == doc_id))
            document = result.scalar_one_or_none()

            if not document:
                return {"error": "Document not found"}

            # Update status
            document.status = DocumentStatus.PROCESSING
            await session.commit()

            # Get full path
            doc_path = str(Path(settings.DOCS_ROOT) / document.rel_path)

            # Step 1: OCR
            ocr_task = await _create_task(session, doc_id, TaskStep.OCR)
            try:
                ocr_results = await task_instance.pipeline.process_ocr(doc_path)

                # Save OCR results to pages
                for ocr_data in ocr_results:
                    page = DocumentPage(
                        document_id=doc_id,
                        page_index=ocr_data["page_index"],
                        ocr_text=ocr_data["text"],
                        bbox_json=ocr_data.get("bbox_data"),
                    )
                    session.add(page)

                document.page_count = len(ocr_results)
                await _complete_task(session, ocr_task)
                await session.commit()
            except Exception as e:
                await _fail_task(session, ocr_task, str(e))
                raise

            # Step 2: Summarize
            summary_task = await _create_task(session, doc_id, TaskStep.SUMMARIZE)
            try:
                # Combine all OCR text
                full_text = "\n\n".join([r["text"] for r in ocr_results if r.get("text")])

                if full_text.strip():
                    summary_result = await task_instance.pipeline.process_summary(full_text)

                    # Save summary
                    summary = DocumentSummary(
                        document_id=doc_id,
                        summary_md=summary_result.get("summary_md"),
                        keywords=summary_result.get("keywords", []),
                        structured=summary_result.get("structured", {}),
                        provider={"model": settings.LLM_MODEL, "provider": settings.LLM_PROVIDER},
                    )
                    session.add(summary)

                await _complete_task(session, summary_task)
                await session.commit()
            except Exception as e:
                await _fail_task(session, summary_task, str(e))
                # Continue even if summary fails

            # Step 3: Embeddings
            embed_task = await _create_task(session, doc_id, TaskStep.EMBED)
            try:
                embeddings = await task_instance.pipeline.process_embeddings(doc_id, ocr_results)

                # Save embedding metadata
                for emb_data in embeddings:
                    emb = Embedding(
                        document_id=doc_id,
                        page_index=emb_data["page_index"],
                        chunk_id=emb_data["chunk_id"],
                        embedding_key=emb_data["embedding_key"],
                        dim=emb_data["dim"],
                        text_excerpt=emb_data["text_excerpt"],
                        provider={"model": settings.EMBED_MODEL, "provider": settings.EMBED_PROVIDER},
                    )
                    session.add(emb)

                await _complete_task(session, embed_task)
                await session.commit()
            except Exception as e:
                await _fail_task(session, embed_task, str(e))
                # Continue even if embedding fails

            # Step 4: Thumbnail
            thumb_task = await _create_task(session, doc_id, TaskStep.THUMBNAIL)
            try:
                thumb_dir = str(Path(settings.THUMBS_ROOT) / str(doc_id))
                thumb_paths = await task_instance.pipeline.process_thumbnail(doc_path, thumb_dir)

                # Update pages with thumbnail paths
                for idx, thumb_path in enumerate(thumb_paths):
                    rel_thumb = str(Path(thumb_path).relative_to(settings.THUMBS_ROOT))
                    page_result = await session.execute(
                        select(DocumentPage).where(
                            DocumentPage.document_id == doc_id, DocumentPage.page_index == idx
                        )
                    )
                    page = page_result.scalar_one_or_none()
                    if page:
                        page.thumb_rel_path = rel_thumb

                await _complete_task(session, thumb_task)
                await session.commit()
            except Exception as e:
                await _fail_task(session, thumb_task, str(e))

            # Step 5: Preview
            preview_task = await _create_task(session, doc_id, TaskStep.PREVIEW)
            try:
                preview_dir = str(Path(settings.PREVIEWS_ROOT) / str(doc_id))
                preview_paths = await task_instance.pipeline.process_preview(doc_path, preview_dir)

                # Update pages with preview paths
                for idx, preview_path in enumerate(preview_paths):
                    rel_preview = str(Path(preview_path).relative_to(settings.PREVIEWS_ROOT))
                    page_result = await session.execute(
                        select(DocumentPage).where(
                            DocumentPage.document_id == doc_id, DocumentPage.page_index == idx
                        )
                    )
                    page = page_result.scalar_one_or_none()
                    if page:
                        page.preview_rel_path = rel_preview

                await _complete_task(session, preview_task)
                await session.commit()
            except Exception as e:
                await _fail_task(session, preview_task, str(e))

            # Mark document as ready
            document.status = DocumentStatus.READY
            await session.commit()

            return {"status": "success", "document_id": str(doc_id)}

        except Exception as e:
            # Mark document as error
            document.status = DocumentStatus.ERROR
            document.error = str(e)
            await session.commit()
            raise


async def _create_task(session, document_id: UUID, step: TaskStep) -> TaskModel:
    """Create a new task"""
    task = TaskModel(
        document_id=document_id,
        step=step,
        status=TaskStatus.RUNNING,
        started_at=datetime.utcnow(),
    )
    session.add(task)
    await session.flush()
    return task


async def _complete_task(session, task: TaskModel):
    """Mark task as complete"""
    task.status = TaskStatus.SUCCESS
    task.finished_at = datetime.utcnow()


async def _fail_task(session, task: TaskModel, error: str):
    """Mark task as failed"""
    task.status = TaskStatus.FAILED
    task.error = error
    task.finished_at = datetime.utcnow()
    await session.flush()
