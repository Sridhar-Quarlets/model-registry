from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.models.model import ModelStatus, ModelType


class ModelBase(BaseModel):
    model_name: str = Field(..., max_length=150)
    display_name: str = Field(..., max_length=200)
    version: str = Field(..., max_length=20)
    model_type: ModelType
    domain: str = Field(..., max_length=50)
    tags: Optional[str] = None
    artifact_path: str = Field(..., max_length=255)
    model_format: str = Field(..., max_length=50)


class ModelCreate(ModelBase):
    parent_model_id: Optional[UUID] = None
    source_repo: Optional[str] = Field(None, max_length=255)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    dataset_name: Optional[str] = Field(None, max_length=150)
    dataset_version: Optional[str] = Field(None, max_length=50)
    training_parameters: Optional[Dict[str, Any]] = None
    framework: Optional[str] = Field(None, max_length=50)
    hardware_used: Optional[str] = Field(None, max_length=100)
    metrics: Optional[Dict[str, Any]] = None
    benchmark_dataset: Optional[str] = Field(None, max_length=150)
    checksum: str = Field(..., max_length=64)
    resource_requirements: Optional[Dict[str, Any]] = None
    env_type: Optional[str] = Field(None, max_length=20)


class ModelUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=200)
    tags: Optional[str] = None
    status: Optional[ModelStatus] = None
    metrics: Optional[Dict[str, Any]] = None
    inference_endpoint: Optional[str] = Field(None, max_length=255)
    resource_requirements: Optional[Dict[str, Any]] = None
    reviewer: Optional[str] = Field(None, max_length=100)
    approval_notes: Optional[str] = None


class ModelResponse(ModelBase):
    model_id: UUID
    parent_model_id: Optional[UUID]
    source_repo: Optional[str]
    input_schema: Optional[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]
    dependencies: Optional[Dict[str, Any]]
    dataset_name: Optional[str]
    dataset_version: Optional[str]
    training_parameters: Optional[Dict[str, Any]]
    framework: Optional[str]
    hardware_used: Optional[str]
    metrics: Optional[Dict[str, Any]]
    benchmark_dataset: Optional[str]
    status: ModelStatus
    created_by: str
    created_at: datetime
    last_updated_at: Optional[datetime]
    reviewer: Optional[str]
    approval_notes: Optional[str]
    checksum: str
    encryption_status: bool
    signed_by: Optional[str]
    access_policy_id: Optional[UUID]
    inference_endpoint: Optional[str]
    resource_requirements: Optional[Dict[str, Any]]
    last_accessed: Optional[datetime]
    access_count: int
    usage_stats: Optional[Dict[str, Any]]
    env_type: Optional[str]

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    models: List[ModelResponse]
    total: int
    page: int
    size: int


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class AccessPolicyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    rules: Dict[str, Any]


class AccessPolicyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    rules: Dict[str, Any]
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True