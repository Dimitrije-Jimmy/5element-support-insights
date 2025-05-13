"""OpenAI chat wrapper — *only* instantiated if a key is present."""
from typing import List

from openai import OpenAI
from loguru import logger

from ..config import settings


class OpenAIService:
    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        self.client = OpenAI(api_key=api_key)

    async def chat(
        self,
        prompt: str,
        history: List[str] | None = None,
        tools: list[dict] | None = None,    # ← accept tools
    ) -> dict | str:
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools or None,            # ← pass through if provided
            tool_choice="auto" if tools else None,
        )
        msg = response.choices[0].message
        # if a function was called, return its payload for the caller to parse
        if getattr(msg, "tool_calls", None):
            return {"tool_call": msg.tool_calls[0].to_dict()}
        return msg.content.strip()