"""Document processing pipeline"""
import re
from pathlib import Path
from typing import List
from uuid import UUID
from app.config import get_settings
from app.services.ocr import get_ocr_service
from app.services.llm import get_llm_service
from app.services.embed import get_embedding_service
from app.services.vector import get_vector_store, VectorItem
from app.services.preview import PreviewRenderer

settings = get_settings()


class DocumentPipeline:
    """Document processing pipeline"""

    def __init__(self):
        self.ocr_service = get_ocr_service()
        self.llm_service = get_llm_service()
        self.embed_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.preview_renderer = PreviewRenderer()

    async def process_ocr(self, document_path: str) -> List[dict]:
        """Process OCR for document"""
        file_ext = Path(document_path).suffix.lower()

        if file_ext == ".pdf":
            results = await self.ocr_service.process_pdf(document_path)
            return [
                {
                    "page_index": r.page_index,
                    "text": r.text,
                    "bbox_data": r.bbox_data,
                }
                for r in results
            ]
        else:
            # Image file
            text = await self.ocr_service.process_image(document_path)
            return [{"page_index": 0, "text": text, "bbox_data": None}]

    async def process_summary(self, full_text: str) -> dict:
        """Process summary for document"""
        result = await self.llm_service.summarize(full_text)
        return result

    async def process_embeddings(self, document_id: UUID, pages_text: List[dict]) -> List[dict]:
        """Process embeddings for document pages"""
        embeddings = []

        for page_data in pages_text:
            page_index = page_data["page_index"]
            text = page_data["text"]

            if not text or len(text.strip()) < 10:
                continue

            # Split text into chunks
            chunks = self._chunk_text(text, settings.EMBED_CHUNK_TOKENS, settings.EMBED_CHUNK_OVERLAP)

            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                vector = await self.embed_service.embed_text(chunk)

                embedding_key = f"{document_id}_{page_index}_{chunk_idx}"
                embeddings.append(
                    {
                        "page_index": page_index,
                        "chunk_id": f"{page_index}_{chunk_idx}",
                        "embedding_key": embedding_key,
                        "vector": vector,
                        "text_excerpt": chunk[:500],  # Store excerpt
                        "dim": len(vector),
                    }
                )

        # Upsert to vector store
        if embeddings:
            vector_items = [
                VectorItem(
                    id=emb["embedding_key"],
                    vector=emb["vector"],
                    metadata={
                        "document_id": str(document_id),
                        "page_index": emb["page_index"],
                        "chunk_id": emb["chunk_id"],
                        "text": emb["text_excerpt"],
                    },
                )
                for emb in embeddings
            ]
            await self.vector_store.upsert(vector_items)

        return embeddings

    async def process_preview(self, document_path: str, output_dir: str) -> List[str]:
        """Generate preview images"""
        file_ext = Path(document_path).suffix.lower()

        if file_ext == ".pdf":
            return await self.preview_renderer.generate_pdf_previews(document_path, output_dir)
        else:
            # For images, just copy or generate a preview
            output_path = str(Path(output_dir) / "page_0.png")
            return [output_path]

    async def process_thumbnail(self, document_path: str, output_dir: str) -> List[str]:
        """Generate thumbnail images"""
        file_ext = Path(document_path).suffix.lower()

        if file_ext == ".pdf":
            return await self.preview_renderer.generate_pdf_thumbnails(document_path, output_dir)
        else:
            output_path = str(Path(output_dir) / f"thumb_0.{settings.THUMBNAIL_FORMAT}")
            await self.preview_renderer.generate_image_thumbnail(document_path, output_path)
            return [output_path]

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
        """Split text into chunks by approximate token count"""
        # Simple word-based chunking (approximate tokens)
        words = text.split()
        chunks = []

        # Approximate: 1 token ≈ 0.75 words for English, may vary for Chinese
        words_per_chunk = int(chunk_size * 0.75)
        overlap_words = int(overlap * 0.75)

        for i in range(0, len(words), words_per_chunk - overlap_words):
            chunk_words = words[i : i + words_per_chunk]
            if chunk_words:
                chunks.append(" ".join(chunk_words))

        return chunks if chunks else [text]
