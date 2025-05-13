from collections import deque
from ..config import settings

# naive in‑process memory – swap for Redis if scaling
_sessions: dict[str, deque] = {}

def remember(session_id: str, query: str):
    dq = _sessions.setdefault(session_id, deque(maxlen=settings.MEMORY_WINDOW))
    dq.append(query)

def recall(session_id: str) -> str:
    dq = _sessions.get(session_id, deque())
    return " | ".join(dq)