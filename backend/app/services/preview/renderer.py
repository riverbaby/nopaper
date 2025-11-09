"""Document preview and thumbnail renderer"""
import asyncio
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from PIL import Image
from app.config import get_settings
from app.utils.fs import ensure_dir

settings = get_settings()


class PreviewRenderer:
    """Document preview and thumbnail renderer"""

    async def generate_pdf_previews(self, pdf_path: str, output_dir: str) -> List[str]:
        """Generate preview images for each PDF page"""
        loop = asyncio.get_event_loop()
        paths = await loop.run_in_executor(None, self._generate_pdf_previews_sync, pdf_path, output_dir)
        return paths

    def _generate_pdf_previews_sync(self, pdf_path: str, output_dir: str) -> List[str]:
        """Synchronous PDF preview generation"""
        ensure_dir(output_dir)
        doc = fitz.open(pdf_path)
        preview_paths = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Render at specified DPI
            zoom = settings.PREVIEW_DPI / 72  # 72 is the default DPI
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Save as PNG
            output_path = str(Path(output_dir) / f"page_{page_num}.png")
            pix.save(output_path)
            preview_paths.append(output_path)

        doc.close()
        return preview_paths

    async def generate_pdf_thumbnails(self, pdf_path: str, output_dir: str) -> List[str]:
        """Generate thumbnail images for each PDF page"""
        loop = asyncio.get_event_loop()
        paths = await loop.run_in_executor(None, self._generate_pdf_thumbnails_sync, pdf_path, output_dir)
        return paths

    def _generate_pdf_thumbnails_sync(self, pdf_path: str, output_dir: str) -> List[str]:
        """Synchronous PDF thumbnail generation"""
        ensure_dir(output_dir)
        doc = fitz.open(pdf_path)
        thumbnail_paths = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Render at higher resolution first
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Resize to thumbnail
            img.thumbnail((settings.THUMBNAIL_MAX_WIDTH, settings.THUMBNAIL_MAX_WIDTH * 2))

            # Save as WebP or JPEG
            output_path = str(Path(output_dir) / f"thumb_{page_num}.{settings.THUMBNAIL_FORMAT}")
            if settings.THUMBNAIL_FORMAT == "webp":
                img.save(output_path, "WEBP", quality=85)
            else:
                img.save(output_path, "JPEG", quality=85)

            thumbnail_paths.append(output_path)

        doc.close()
        return thumbnail_paths

    async def generate_image_thumbnail(self, image_path: str, output_path: str) -> str:
        """Generate thumbnail for an image file"""
        loop = asyncio.get_event_loop()
        path = await loop.run_in_executor(None, self._generate_image_thumbnail_sync, image_path, output_path)
        return path

    def _generate_image_thumbnail_sync(self, image_path: str, output_path: str) -> str:
        """Synchronous image thumbnail generation"""
        ensure_dir(Path(output_path).parent)

        img = Image.open(image_path)
        img.thumbnail((settings.THUMBNAIL_MAX_WIDTH, settings.THUMBNAIL_MAX_WIDTH * 2))

        if settings.THUMBNAIL_FORMAT == "webp":
            img.save(output_path, "WEBP", quality=85)
        else:
            img.save(output_path, "JPEG", quality=85)

        return output_path
