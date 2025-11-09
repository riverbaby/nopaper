"""LLM services"""
from app.config import get_settings
from .base import LLMService, LLMResponse
from .ollama import OllamaLLMService

settings = get_settings()


def get_llm_service() -> LLMService:
    """Get LLM service instance based on configuration"""
    if settings.LLM_PROVIDER == "ollama":
        return OllamaLLMService()
    # Add other implementations here (openai_compatible, deepseek, etc.)
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


__all__ = ["LLMService", "LLMResponse", "get_llm_service"]
