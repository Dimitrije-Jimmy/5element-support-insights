"""Google Gemini chat wrapper — needs google-generativeai pip package."""
from typing import List
from functools import lru_cache

from loguru import logger
import google.generativeai as genai

from ..config import settings

LLM_MODEL = "models/gemini-1.5-flash-latest"   # or -1.5-pro-latest
MODEL_NAME = "models/gemini-1.5-flash-latest"


class GeminiService:
    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing")
        genai.configure(api_key=api_key)
        self.model = _get_client()

    async def chat(
        self,
        prompt: str,
        history: List[str] | None = None,
        tools: list[dict] | None = None,    # ← ignore, Gemini SDK lacks tools
    ) -> str:
        resp = self.model.generate_content(prompt)
        return resp.text.strip()

@lru_cache()
def _get_client():
    return genai.GenerativeModel(MODEL_NAME)
