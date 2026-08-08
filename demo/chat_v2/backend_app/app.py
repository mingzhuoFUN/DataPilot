from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.chat import router as chat_router
from .routers.export import router as export_router
from .routers.workspace import router as workspace_router
from .services.docker_executor import ensure_execution_backend_ready, shutdown_execution_backend
from .settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_execution_backend_ready()
    try:
        yield
    finally:
        shutdown_execution_backend()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials="*" not in settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(workspace_router)
    app.include_router(chat_router)
    app.include_router(export_router)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
            "provider": settings.default_provider,
            "execution_mode": settings.execution_mode,
        }

    return app


app = create_app()
