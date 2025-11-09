"""Base LLM interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response"""

    text: str
    metadata: Optional[Dict[str, Any]] = None


class LLMService(ABC):
    """Abstract LLM service interface"""

    @abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate text from prompt"""
        pass

    @abstractmethod
    async def summarize(self, text: str) -> Dict[str, Any]:
        """Summarize document text"""
        pass
