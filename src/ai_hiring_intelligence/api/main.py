from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from ai_hiring_intelligence import __version__
from ai_hiring_intelligence.api.routes import health, metadata
from ai_hiring_intelligence.core.config import get_settings
from ai_hiring_intelligence.core.logging import configure_logging, get_logger, log_extra

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info(
        "api_startup",
        extra=log_extra(app_name=settings.app_name, environment=settings.app_env),
    )
    yield
    logger.info(
        "api_shutdown",
        extra=log_extra(app_name=settings.app_name, environment=settings.app_env),
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="AI Hiring Intelligence API boilerplate.",
        lifespan=lifespan,
    )
    app.include_router(health.router, tags=["health"])
    app.include_router(metadata.router, prefix="/v1", tags=["metadata"])
    return app


app = create_app()
