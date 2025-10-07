from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.model import User
from app.services.model_service import ModelService

router = APIRouter()


@router.get("/{model_id}")
def get_model_metrics(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    model = service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return {
        "model_id": model_id,
        "metrics": model.metrics,
        "usage_stats": model.usage_stats,
        "access_count": model.access_count,
        "last_accessed": model.last_accessed
    }


@router.post("/{model_id}/access")
def record_model_access(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    success = service.record_access(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Access recorded"}