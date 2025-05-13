from datetime import datetime
from pydantic import BaseModel, Field

class MessageIn(BaseModel):
    id_user: int
    timestamp: datetime
    source: str
    message: str

class MessageOut(MessageIn):
    id: str
    category: str | None = None

class QueryFilters(BaseModel):
    category: str | None = None
    source: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

class ChatRequest(BaseModel):
    query: str
    session_id: str = Field(..., description="Client‑provided session identifier")