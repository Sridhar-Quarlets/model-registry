from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/model_registry",
        description="PostgreSQL database URL"
    )
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration")

    S3_BUCKET: str = Field(default="quarlets-models", description="S3 bucket for model artifacts")
    S3_ENDPOINT_URL: str = Field(default=None, description="S3 endpoint URL (for MinIO)")
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS access key")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS secret key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")

    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="CORS allowed hosts")

    MLFLOW_TRACKING_URI: str = Field(
        default="http://localhost:5000",
        description="MLflow tracking server URI"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()