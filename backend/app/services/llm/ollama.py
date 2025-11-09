"""Ollama LLM implementation"""
import json
import httpx
from typing import Dict, Any, Optional
from app.config import get_settings
from .base import LLMService, LLMResponse

settings = get_settings()

SUMMARIZE_PROMPT = """You are a meticulous document assistant. Generate a structured summary for the given text:
- Title (generate one if not present)
- 3-6 key points (concise and scannable)
- Keywords (hashtag style)
- Extract dates, amounts, invoice numbers, parties, and other relevant information into JSON fields

Output in Markdown format, with a JSON code block at the end containing only the extracted fields.

Text content:
{text}
"""


class OllamaLLMService(LLMService):
    """Ollama LLM service implementation"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate text from prompt"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", settings.LLM_TEMPERATURE),
                "num_predict": kwargs.get("max_tokens", settings.LLM_MAX_TOKENS),
            },
        }

        if system:
            payload["system"] = system

        response = await self.client.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()

        data = response.json()
        return LLMResponse(text=data.get("response", ""), metadata=data)

    async def summarize(self, text: str) -> Dict[str, Any]:
        """Summarize document text"""
        prompt = SUMMARIZE_PROMPT.format(text=text[:8000])  # Limit text length
        response = await self.generate(prompt)

        # Extract JSON from response
        structured = {}
        try:
            # Find JSON code block
            if "```json" in response.text:
                json_start = response.text.find("```json") + 7
                json_end = response.text.find("```", json_start)
                json_str = response.text[json_start:json_end].strip()
                structured = json.loads(json_str)
            elif "```" in response.text:
                json_start = response.text.find("```") + 3
                json_end = response.text.find("```", json_start)
                json_str = response.text[json_start:json_end].strip()
                structured = json.loads(json_str)
        except Exception:
            pass

        # Extract keywords from response
        keywords = []
        for line in response.text.split("\n"):
            if line.strip().startswith("#") and not line.startswith("##"):
                # Extract hashtags
                words = [w.strip("#") for w in line.split() if w.startswith("#")]
                keywords.extend(words)

        return {
            "summary_md": response.text,
            "keywords": keywords,
            "structured": structured,
        }
