"""PaddleOCR implementation"""
from typing import List
import asyncio
from pathlib import Path
from paddleocr import PaddleOCR
import fitz  # PyMuPDF
from app.config import get_settings
from .base import OCRService, OCRResult

settings = get_settings()


class PaddleOCRService(OCRService):
    """PaddleOCR service implementation"""

    def __init__(self):
        langs = [lang.strip() for lang in settings.OCR_LANGS.split(",")]
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=langs[0] if langs else "ch",
            show_log=False,
        )

    async def process_pdf(self, pdf_path: str) -> List[OCRResult]:
        """Process PDF and return OCR results for each page"""
        results = []

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        pdf_results = await loop.run_in_executor(None, self._process_pdf_sync, pdf_path)

        return pdf_results

    def _process_pdf_sync(self, pdf_path: str) -> List[OCRResult]:
        """Synchronous PDF processing"""
        results = []
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better OCR
            img_path = f"/tmp/page_{page_num}.png"
            pix.save(img_path)

            # Run OCR
            ocr_result = self.ocr.ocr(img_path, cls=True)

            # Extract text
            text_lines = []
            bbox_data = []
            if ocr_result and ocr_result[0]:
                for line in ocr_result[0]:
                    if line:
                        bbox, (text, confidence) = line
                        text_lines.append(text)
                        bbox_data.append({"bbox": bbox, "text": text, "confidence": confidence})

            text = "\n".join(text_lines)
            results.append(OCRResult(page_index=page_num, text=text, bbox_data=bbox_data))

            # Clean up temp file
            Path(img_path).unlink(missing_ok=True)

        doc.close()
        return results

    async def process_image(self, image_path: str) -> str:
        """Process single image and return OCR text"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._process_image_sync, image_path)
        return result

    def _process_image_sync(self, image_path: str) -> str:
        """Synchronous image processing"""
        ocr_result = self.ocr.ocr(image_path, cls=True)

        text_lines = []
        if ocr_result and ocr_result[0]:
            for line in ocr_result[0]:
                if line:
                    _, (text, _) = line
                    text_lines.append(text)

        return "\n".join(text_lines)
