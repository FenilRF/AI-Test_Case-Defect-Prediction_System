"""
FastAPI Application Entry Point
=================================
Initialises the app, registers routers, configures CORS,
creates DB tables, and sets up logging.
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import Base, engine
from app.api.requirements import router as requirements_router
from app.api.defect_prediction import router as defect_prediction_router
from app.api.design_upload import router as design_upload_router

# ── Settings ─────────────────────────────────────────────────
settings = get_settings()

# ── Logging Configuration ────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format=settings.LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Database Table Creation ──────────────────────────────────
# Creates tables if they don't exist — safe for development.
Base.metadata.create_all(bind=engine)
logger.info("Database tables created / verified.")

# ── Requirement Folder Storage ───────────────────────────────
from app.services.folder_storage_service import ensure_base_dir
ensure_base_dir()
logger.info("Requirement folder storage directory verified.")

# ── FastAPI Application ──────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered system for automated test case generation from NLP-parsed "
        "requirements and ML-based defect prediction with risk prioritisation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────────
app.include_router(requirements_router)
app.include_router(defect_prediction_router)
app.include_router(design_upload_router)


# ── Health Check ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


logger.info("%s v%s is ready.", settings.APP_NAME, settings.APP_VERSION)
