from fastapi import APIRouter

from ai_hiring_intelligence import __version__
from ai_hiring_intelligence.core.config import get_settings
from ai_hiring_intelligence.schemas.metadata import ServiceMetadata

router = APIRouter()


@router.get("/metadata", response_model=ServiceMetadata)
async def service_metadata() -> ServiceMetadata:
    settings = get_settings()
    return ServiceMetadata(
        name=settings.app_name,
        environment=settings.app_env,
        version=__version__,
    )

