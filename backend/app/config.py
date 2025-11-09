"""Application configuration"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Core
    APP_SECRET: str = "change_me_in_production"
    APP_BASE_URL: str = "http://localhost:8080"
    APP_NAME: str = "DocNest"
    DEBUG: bool = False

    # Storage
    DOCS_ROOT: str = "/data/docs"
    THUMBS_ROOT: str = "/data/thumbs"
    PREVIEWS_ROOT: str = "/data/previews"
    MAX_UPLOAD_MB: int = 1024

    # Postgres
    PG_HOST: str = "postgres"
    PG_PORT: int = 5432
    PG_DB: str = "docnest"
    PG_USER: str = "docnest"
    PG_PASSWORD: str = "docnest"
    PG_SSLMODE: str = "disable"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Vector Store
    VECTOR_BACKEND: str = "qdrant"  # qdrant | pgvector | weaviate | chroma | milvus
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "docnest_chunks"

    # OCR
    OCR_ENGINE: str = "paddleocr"  # paddleocr | deepseek-ocr | tesseract
    OCR_LANGS: str = "ch,en"
    OCR_PAGE_PARALLELISM: int = 2

    # LLM (summarize/RAG)
    LLM_PROVIDER: str = "ollama"  # ollama | openai_compatible | deepseek
    LLM_MODEL: str = "qwen2.5:7b-instruct"
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.1
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # Embedding
    EMBED_PROVIDER: str = "local_service"  # local_service | openai_compatible
    EMBED_MODEL: str = "BAAI/bge-m3"
    EMBED_NORMALIZE: bool = True
    EMBED_CHUNK_TOKENS: int = 512
    EMBED_CHUNK_OVERLAP: int = 64

    # Processing
    THUMBNAIL_MAX_WIDTH: int = 600
    THUMBNAIL_FORMAT: str = "webp"
    PREVIEW_DPI: int = 150

    # Worker
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
