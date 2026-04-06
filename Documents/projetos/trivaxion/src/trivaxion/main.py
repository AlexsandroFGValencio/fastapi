from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from trivaxion.adapters.inbound.http import (
    admin_routes,
    analysis_routes,
    auth_routes,
    dashboard_routes,
    search_routes,
    user_routes,
)
from trivaxion.adapters.inbound.web.routes import web_routes
from trivaxion.infrastructure.config.settings import get_settings
from trivaxion.infrastructure.db.base import init_db
from trivaxion.infrastructure.logging.logger import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # Add session middleware for web routes
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret_key,
        session_cookie="trivaxion_session",
        max_age=86400,  # 24 hours
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # API routes (prefixed with /api/v1)
    app.include_router(auth_routes.router, prefix="/api/v1")
    app.include_router(user_routes.router, prefix="/api/v1")
    app.include_router(analysis_routes.router, prefix="/api/v1")
    app.include_router(search_routes.router, prefix="/api/v1")
    app.include_router(admin_routes.router, prefix="/api/v1")
    app.include_router(dashboard_routes.router, prefix="/api/v1")
    
    # Filiais routes
    from trivaxion.adapters.inbound.http import filiais_routes
    app.include_router(filiais_routes.router)
    
    # Web routes (no prefix - serves HTML)
    app.include_router(web_routes.router)
    
    return app


app = create_app()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api")
async def api_root() -> dict[str, str]:
    return {"message": "Trivaxion API", "version": "0.1.0"}
