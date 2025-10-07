from sqlalchemy import Column, String, Text, Boolean, Integer, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ModelStatus(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class ModelType(str, enum.Enum):
    TRANSFORMER = "Transformer"
    GNN = "GNN"
    SLM = "SLM"
    REGRESSION = "Regression"
    ENSEMBLE = "Ensemble"


class ModelRegistryEntry(Base):
    __tablename__ = "model_registry"

    # Identity fields
    model_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(150), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)

    # Versioning
    version = Column(String(20), nullable=False)
    parent_model_id = Column(UUID(as_uuid=True), nullable=True)
    source_repo = Column(String(255), nullable=True)

    # Model Type & Category
    model_type = Column(Enum(ModelType), nullable=False)
    domain = Column(String(50), nullable=False)
    tags = Column(Text, nullable=True)

    # Artifact Details
    artifact_path = Column(String(255), nullable=False)
    model_format = Column(String(50), nullable=False)
    input_schema = Column(JSONB, nullable=True)
    output_schema = Column(JSONB, nullable=True)
    dependencies = Column(JSONB, nullable=True)

    # Training Details
    dataset_name = Column(String(150), nullable=True)
    dataset_version = Column(String(50), nullable=True)
    training_parameters = Column(JSONB, nullable=True)
    framework = Column(String(50), nullable=True)
    hardware_used = Column(String(100), nullable=True)

    # Performance Metrics
    metrics = Column(JSONB, nullable=True)
    benchmark_dataset = Column(String(150), nullable=True)

    # Lifecycle & Governance
    status = Column(Enum(ModelStatus), nullable=False, default=ModelStatus.DEVELOPMENT)
    created_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    reviewer = Column(String(100), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Security & Integrity
    checksum = Column(String(64), nullable=False)
    encryption_status = Column(Boolean, default=False)
    signed_by = Column(String(100), nullable=True)
    access_policy_id = Column(UUID(as_uuid=True), nullable=True)

    # Runtime Details
    inference_endpoint = Column(String(255), nullable=True)
    resource_requirements = Column(JSONB, nullable=True)

    # Audit & Logs
    last_accessed = Column(TIMESTAMP(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    usage_stats = Column(JSONB, nullable=True)

    # Environment
    env_type = Column(String(20), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="consumer")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class AccessPolicy(Base):
    __tablename__ = "access_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rules = Column(JSONB, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())