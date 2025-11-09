"""Base OCR interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class OCRResult:
    """OCR result for a single page"""

    page_index: int
    text: str
    bbox_data: List[Dict[str, Any]] = None  # Optional bounding box data


class OCRService(ABC):
    """Abstract OCR service interface"""

    @abstractmethod
    async def process_pdf(self, pdf_path: str) -> List[OCRResult]:
        """Process PDF and return OCR results for each page"""
        pass

    @abstractmethod
    async def process_image(self, image_path: str) -> str:
        """Process single image and return OCR text"""
        pass
