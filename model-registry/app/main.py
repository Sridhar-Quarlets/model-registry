from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, create_tables
from app.routers import models, auth, metrics
from app.routers import ui as ui_routes

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Quarlets Model Registry",
    description="Central repository for AI/ML model management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable cookie-based sessions for the UI
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Serve static assets for the UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
# Jinja UI routes
app.include_router(ui_routes.router, prefix="/ui", tags=["UI"])


@app.get("/")
async def root():
    return {"message": "Quarlets Model Registry API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}