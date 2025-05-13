"""Service factory + protocol used by FastAPI."""
from typing import Protocol

from ..config import settings
from .openai_service import OpenAIService
from .gemini_service import GeminiService
from .huggingface_service import HFService


class LLMServiceProtocol(Protocol):
    async def chat(
        self,
        prompt: str,
        history: list[str] | None = None,
        tools: list[dict] | None = None,   # ← new, optional
    ) -> dict | str: ...

def get_llm_service() -> LLMServiceProtocol:
    provider = settings.resolved_provider
    if provider == "openai":
        return OpenAIService(settings.OPENAI_API_KEY)
    if provider == "gemini":
        return GeminiService(settings.GEMINI_API_KEY)
    return HFService(settings.HF_API_KEY, settings.HF_MODEL_ID)
