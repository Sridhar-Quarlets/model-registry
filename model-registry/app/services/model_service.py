from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
from uuid import UUID
from datetime import datetime

from app.models.model import ModelRegistryEntry, ModelStatus, ModelType
from app.schemas.model import ModelCreate, ModelUpdate


class ModelService:
    def __init__(self, db: Session):
        self.db = db

    def register_model(self, model: ModelCreate, created_by: str) -> ModelRegistryEntry:
        db_model = ModelRegistryEntry(
            **model.dict(),
            created_by=created_by
        )
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return db_model

    def get_model_by_id(self, model_id: UUID) -> Optional[ModelRegistryEntry]:
        return self.db.query(ModelRegistryEntry).filter(
            ModelRegistryEntry.model_id == model_id
        ).first()

    def get_latest_model(
        self,
        model_type: Optional[ModelType] = None,
        domain: Optional[str] = None
    ) -> Optional[ModelRegistryEntry]:
        query = self.db.query(ModelRegistryEntry).filter(
            ModelRegistryEntry.status == ModelStatus.PRODUCTION
        )

        if model_type:
            query = query.filter(ModelRegistryEntry.model_type == model_type)
        if domain:
            query = query.filter(ModelRegistryEntry.domain == domain)

        return query.order_by(desc(ModelRegistryEntry.created_at)).first()

    def promote_model(
        self,
        model_id: UUID,
        target_status: ModelStatus,
        reviewer: str
    ) -> bool:
        model = self.get_model_by_id(model_id)
        if not model:
            return False

        model.status = target_status
        model.reviewer = reviewer
        model.last_updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def list_models(
        self,
        model_type: Optional[ModelType] = None,
        domain: Optional[str] = None,
        status: Optional[ModelStatus] = None,
        tags: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[ModelRegistryEntry], int]:
        query = self.db.query(ModelRegistryEntry)

        if model_type:
            query = query.filter(ModelRegistryEntry.model_type == model_type)
        if domain:
            query = query.filter(ModelRegistryEntry.domain == domain)
        if status:
            query = query.filter(ModelRegistryEntry.status == status)
        if tags:
            query = query.filter(ModelRegistryEntry.tags.contains(tags))

        total = query.count()
        models = query.order_by(desc(ModelRegistryEntry.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()

        return models, total

    def search_models(
        self,
        query: str,
        domain: Optional[str] = None,
        model_type: Optional[ModelType] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[ModelRegistryEntry], int]:
        db_query = self.db.query(ModelRegistryEntry).filter(
            or_(
                ModelRegistryEntry.model_name.contains(query),
                ModelRegistryEntry.display_name.contains(query),
                ModelRegistryEntry.tags.contains(query)
            )
        )

        if domain:
            db_query = db_query.filter(ModelRegistryEntry.domain == domain)
        if model_type:
            db_query = db_query.filter(ModelRegistryEntry.model_type == model_type)

        total = db_query.count()
        models = db_query.order_by(desc(ModelRegistryEntry.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()

        return models, total

    def update_model(
        self,
        model_id: UUID,
        model_update: ModelUpdate
    ) -> Optional[ModelRegistryEntry]:
        model = self.get_model_by_id(model_id)
        if not model:
            return None

        update_data = model_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        model.last_updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete_model(self, model_id: UUID) -> bool:
        model = self.get_model_by_id(model_id)
        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def record_access(self, model_id: UUID) -> bool:
        model = self.get_model_by_id(model_id)
        if not model:
            return False

        model.access_count += 1
        model.last_accessed = datetime.utcnow()
        self.db.commit()
        return True