from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from typing import Any, Dict, Optional

from app.services.plannings_analyzer import analyze_planning_from_url, PlanningAnalysisError

router = APIRouter(prefix="/plannings", tags=["plannings"])

class AnalyzeRequest(BaseModel):
    url: Optional[AnyHttpUrl] = None

class AnalyzeResponse(BaseModel):
    ok: bool
    data: Dict[str, Any] | None = None
    message: Optional[str] = None

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_planning(req: AnalyzeRequest):
    try:
        if not req.url:
            raise HTTPException(status_code=400, detail="Champ 'url' manquant.")
        result = await analyze_planning_from_url(str(req.url))
        return AnalyzeResponse(ok=True, data=result)
    except PlanningAnalysisError as exc:
        return AnalyzeResponse(ok=False, message=exc.user_message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur interne pendant l'analyse: {exc}")
