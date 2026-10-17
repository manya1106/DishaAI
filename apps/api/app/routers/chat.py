from fastapi import APIRouter

from ..ai.chat import chat_orchestrator
from ..routers.analyses import compute_analysis, decode_analysis_id
from ..schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/analyses", tags=["Chat"])


@router.post("/{analysis_id}/chat", response_model=ChatResponse)
async def chat_analysis(analysis_id: str, request: ChatRequest):
    analysis = compute_analysis(decode_analysis_id(analysis_id))
    return await chat_orchestrator.handle_chat(analysis, request)
