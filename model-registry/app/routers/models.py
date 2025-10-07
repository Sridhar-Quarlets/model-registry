from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.model import ModelRegistryEntry, User, ModelStatus, ModelType
from app.schemas.model import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelListResponse
)
from app.services.model_service import ModelService

router = APIRouter()


@router.post("/register", response_model=ModelResponse)
def register_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    return service.register_model(model, current_user.email)


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    model = service.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.get("/latest", response_model=ModelResponse)
def get_latest_model(
    model_type: Optional[ModelType] = Query(None),
    domain: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    model = service.get_latest_model(model_type, domain)
    if not model:
        raise HTTPException(status_code=404, detail="No models found")
    return model


@router.post("/promote/{model_id}")
def promote_model(
    model_id: UUID,
    target_status: ModelStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    success = service.promote_model(model_id, target_status, current_user.email)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": f"Model promoted to {target_status.value}"}


@router.get("/", response_model=ModelListResponse)
def list_models(
    model_type: Optional[ModelType] = Query(None),
    domain: Optional[str] = Query(None),
    status: Optional[ModelStatus] = Query(None),
    tags: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    models, total = service.list_models(
        model_type=model_type,
        domain=domain,
        status=status,
        tags=tags,
        page=page,
        size=size
    )
    return ModelListResponse(
        models=models,
        total=total,
        page=page,
        size=size
    )


@router.get("/search")
def search_models(
    q: str = Query(..., description="Search query"),
    domain: Optional[str] = Query(None),
    model_type: Optional[ModelType] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    models, total = service.search_models(
        query=q,
        domain=domain,
        model_type=model_type,
        page=page,
        size=size
    )
    return ModelListResponse(
        models=models,
        total=total,
        page=page,
        size=size
    )


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: UUID,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    updated_model = service.update_model(model_id, model_update)
    if not updated_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return updated_model


@router.delete("/{model_id}")
def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ModelService(db)
    success = service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted successfully"}