"""Fallback local / hosted Hugging Face model."""
from typing import List
from functools import lru_cache

from transformers import pipeline, Pipeline
from loguru import logger

from ..config import settings


class HFService:
    def __init__(self, api_key: str | None, model_id: str):
        self.api_key = api_key
        self.model_id = model_id
        self.pipe = _get_pipeline(task="text-generation",
                                  model_id=model_id,
                                  hf_key=api_key)

    async def chat(
        self,
        prompt: str,
        history: List[str] | None = None,
        tools: list[dict] | None = None,    # ← ignore
    ) -> str:
        out = self.pipe(prompt, max_new_tokens=128, do_sample=True)[0]["generated_text"]
        return out.strip()


@lru_cache()
def _get_pipeline(task: str, model_id: str, hf_key: str | None) -> Pipeline:
    kwargs = {"model": model_id}
    if hf_key:
        kwargs["token"] = hf_key
    return pipeline(task, **kwargs)
