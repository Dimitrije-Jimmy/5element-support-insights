# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .api.v1.endpoints import chatbot, messages, health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A FastAPI backend for 5Element support insight chat.",
        version="1.0.0",
    )
    
    # CORS settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # API routers first
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(messages.router, prefix="/api/v1/messages")
    app.include_router(chatbot.router, prefix="/api/v1/chat")

    # Ensure static directory exists
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Mount static files last
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app

app = create_app()