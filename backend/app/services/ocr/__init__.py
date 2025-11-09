"""OCR services"""
from app.config import get_settings
from .base import OCRService, OCRResult
from .paddleocr import PaddleOCRService

settings = get_settings()


def get_ocr_service() -> OCRService:
    """Get OCR service instance based on configuration"""
    if settings.OCR_ENGINE == "paddleocr":
        return PaddleOCRService()
    # Add other implementations here (deepseek-ocr, tesseract, etc.)
    raise ValueError(f"Unsupported OCR engine: {settings.OCR_ENGINE}")


__all__ = ["OCRService", "OCRResult", "get_ocr_service"]
