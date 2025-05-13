# backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .api.v1.endpoints import chatbot, messages, health

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# API routers first  ✅
app.include_router(health.router)
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(chatbot.router,  prefix="/api/v1/chat",     tags=["chat"])

# Static mount last  ✅
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
