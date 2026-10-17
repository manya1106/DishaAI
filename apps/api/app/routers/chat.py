from fastapi import APIRouter, HTTPException, status
from ..schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/analyses", tags=["Chat"])


@router.post("/{analysis_id}/chat", response_model=ChatResponse)
async def chat_analysis(analysis_id: str, request: ChatRequest):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI verifier and chat orchestrator integration in progress"
    )
