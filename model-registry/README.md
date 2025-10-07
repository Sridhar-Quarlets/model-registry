# Quarlets Model Registry

A comprehensive model registry system for managing AI/ML models with FastAPI backend, PostgreSQL database, and Docker containerization.

## Features

- **Model Management**: Register, version, and manage AI/ML models
- **Metadata Storage**: Comprehensive metadata schema for model tracking
- **Authentication**: OAuth2 + API key authentication
- **Storage Integration**: AWS S3/MinIO for model artifacts
- **MLflow Integration**: Model versioning and experiment tracking
- **Monitoring**: Prometheus + Grafana for performance metrics
- **RESTful APIs**: Complete API endpoints for model operations

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with JSONB support
- **Storage**: AWS S3 / MinIO
- **Authentication**: OAuth2 + JWT
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd model-registry
cp .env.example .env
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- **Model Registry API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **MinIO**: http://localhost:9001 (console)
- **MLflow**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Models
- `POST /models/register` - Register new model
- `GET /models/{id}` - Get model details
- `GET /models/latest` - Get latest model by type
- `POST /models/promote/{id}` - Promote model to production
- `GET /models/` - List models with filters
- `GET /models/search` - Search models
- `PUT /models/{id}` - Update model
- `DELETE /models/{id}` - Delete model

### Metrics
- `GET /metrics/{id}` - Get model metrics
- `POST /metrics/{id}/access` - Record model access

## Model Metadata Schema

The registry stores comprehensive metadata for each model:

- **Identity**: UUID, name, display name
- **Versioning**: Semantic versioning, parent model references
- **Type & Category**: Model type (Transformer, GNN, SLM, etc.), domain
- **Artifacts**: Storage paths, format, input/output schemas
- **Training**: Dataset info, hyperparameters, framework
- **Performance**: Metrics, benchmark results
- **Lifecycle**: Status (dev/staging/production), governance
- **Security**: Checksums, encryption, access policies
- **Runtime**: Resource requirements, inference endpoints
- **Audit**: Access logs, usage statistics

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
export DATABASE_URL="postgresql://postgres:password@localhost:5432/model_registry"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Testing

```bash
pytest tests/
```

## Configuration

Environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `S3_BUCKET`: S3 bucket for model artifacts
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `MLFLOW_TRACKING_URI`: MLflow server URL

## Security Features

- **RBAC**: Role-based access control
- **AES-256**: Encryption for model weights
- **SHA256**: Checksum validation
- **Audit Trails**: Complete access logging
- **JWT Authentication**: Secure API access

## Monitoring

- **Prometheus**: Metrics collection at `/metrics`
- **Grafana**: Dashboard visualization
- **Health Checks**: Service health monitoring
- **Usage Analytics**: Model access tracking

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │   MinIO/S3      │
│   (Port 8000)   │────│   (Port 5432)   │    │   (Port 9000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │     MLflow      │    │   Prometheus    │    │     Grafana     │
         │   (Port 5000)   │    │   (Port 9090)   │    │   (Port 3000)   │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]