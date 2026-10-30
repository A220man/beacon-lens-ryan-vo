from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import api_router
from app.core.config import get_settings
from app.core.database import close_db, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="beacon-lens API — Local generative AI crafting engine",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Serve frontend static files in production/AppImage mode
frontend_static_dir = os.environ.get("FRONTEND_STATIC_DIR")
if frontend_static_dir and os.path.isdir(frontend_static_dir):
    app.mount("/", StaticFiles(directory=frontend_static_dir, html=True), name="frontend")


@app.get("/")
async def root() -> dict:
    if frontend_static_dir and os.path.isdir(frontend_static_dir):
        index_path = os.path.join(frontend_static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"name": settings.app_name, "version": "1.0.0", "docs": "/docs"}

