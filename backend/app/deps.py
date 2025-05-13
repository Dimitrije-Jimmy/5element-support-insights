from fastapi import Depends, Header
from .db import get_db
from .services import memory

async def get_db_conn():
    return get_db()

async def get_session_id(session_id: str | None = Header(default=None)):
    return session_id or "anonymous"