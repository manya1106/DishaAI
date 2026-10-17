from fastapi import APIRouter
from ..config import settings
from ..schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    db_status = "disabled"
    if settings.DATABASE_URL:
        db_status = "configured"

    llm_status = "disabled"
    if settings.LLM_ENABLED and settings.LLM_API_KEY:
        llm_status = "configured"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        data_mode=settings.DATA_MODE,
        db=db_status,
        llm=llm_status
    )
