"""Pydantic data models mapping to both the Supabase `messages` table
and the request/response payloads of the chat endpoint."""
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# ──────────────────────────
# DB-backed message model
# ──────────────────────────
class Source(str, Enum):
    livechat = "livechat"
    telegram = "telegram"


class Message(BaseModel):
    id: str | None = None                # Supabase autogenerates UUID
    id_user: int = Field(..., ge=1)
    timestamp: datetime
    source: Source
    message: str
    category: str | None = None
    created_at: datetime | None = None


# ──────────────────────────
# Chat endpoint DTOs
# ──────────────────────────
class ChatHistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatHistoryItem] = []
    model: str | None = None

class ChatResponse(BaseModel):
    response: str
    context: str | None = None
