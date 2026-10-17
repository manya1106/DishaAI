from fastapi import APIRouter, HTTPException, status
from ..schemas import (
    AnalysisRequest,
    AnalysisResult,
    ReportResponse,
    CompareRequest,
    CompareResult,
)

router = APIRouter(prefix="/api/v1/analyses", tags=["Analyses"])


@router.post("", response_model=AnalysisResult)
async def create_analysis(request: AnalysisRequest):
    # Stub router - replaced by real engine in Agent 3 phase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scoring engine integration in progress"
    )


@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scoring engine integration in progress"
    )


@router.get("/{analysis_id}/locations/{location_id}", response_model=ReportResponse)
async def get_location_report(analysis_id: str, location_id: str):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scoring engine integration in progress"
    )


@router.post("/{analysis_id}/compare", response_model=CompareResult)
async def compare_locations(analysis_id: str, request: CompareRequest):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scoring engine integration in progress"
    )
