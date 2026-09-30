"""
KAVACH AI — Main Application
FastAPI application entry point with CORS, lifecycle, and route registration.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import get_settings
from app.core.exceptions import KavachException
from app.database import close_db, init_db, seed_demo_users_if_missing
from app.api.v1.router import api_router

settings = get_settings()


# ── Lifecycle ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    print("[KAVACH AI] Starting up...")

    # Create required directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    os.makedirs(settings.ai_model_dir, exist_ok=True)
    os.makedirs(settings.scam_patterns_dir, exist_ok=True)

    # Initialize database
    await init_db()
    print("[OK] Database initialized")

    # Seed required demo users if missing (idempotent for production/Render)
    await seed_demo_users_if_missing()

    print("[OK] AI engines loaded")
    print(f"[READY] Server at http://{settings.host}:{settings.port}")
    print(f"[DOCS] API docs at http://{settings.host}:{settings.port}/docs")

    yield

    # Shutdown
    await close_db()
    print("[KAVACH AI] Shutdown complete")


# ── FastAPI App ─────────────────────────────────────────────
app = FastAPI(
    title="KAVACH AI",
    description=(
        "India's AI-Powered Digital Safety Shield — "
        "Defeating Counterfeiting, Fraud & Digital Arrest Scams. "
        "Multi-agent AI platform for citizens, law enforcement, and financial institutions."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],  # Open for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ───────────────────────────────
@app.exception_handler(KavachException)
async def kavach_exception_handler(request: Request, exc: KavachException):
    """Handle all KAVACH custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc) if settings.debug else None,
        },
    )


# ── Register API Routes ────────────────────────────────────
app.include_router(api_router)


# ── Health Check ────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root(request: Request):
    """Root endpoint — serve landing page if browser, else API info."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/frontend/index.html")
    return {
        "name": "KAVACH AI",
        "tagline": "India's AI-Powered Digital Safety Shield",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "frontend": "/frontend/index.html",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
        "ai_modules": [
            "scam_detector",
            "currency_detector",
            "deepfake_detector",
            "fraud_graph",
            "geospatial_intelligence",
        ],
    }

from pathlib import Path
from fastapi.staticfiles import StaticFiles

_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
