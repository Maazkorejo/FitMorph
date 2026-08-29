import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, Base
from app.workers.plateau_worker import start_scheduler, shutdown_scheduler

# Import all API routers
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.exercises import router as exercises_router
from app.api.workouts import router as workouts_router
from app.api.logs import router as logs_router
from app.api.plateau import router as plateau_router
from app.api.physique import router as physique_router
from app.api.reports import router as reports_router
from app.api.coach import router as coach_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist & start background scheduler
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    print(f"[{settings.APP_NAME}] Backend server running and background scheduler started.")
    yield
    # Shutdown: Stop scheduler
    shutdown_scheduler()
    print(f"[{settings.APP_NAME}] Backend server stopped.")

app = FastAPI(
    title="FitMorph API",
    description="Adaptive Fitness Intelligence & Physique Progression Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory for static asset viewing
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(exercises_router, prefix=settings.API_V1_PREFIX)
app.include_router(workouts_router, prefix=settings.API_V1_PREFIX)
app.include_router(logs_router, prefix=settings.API_V1_PREFIX)
app.include_router(plateau_router, prefix=settings.API_V1_PREFIX)
app.include_router(physique_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(coach_router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["Health"])
def health_check():
    """System health check verifying API and database operational status."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "connected"
    }

@app.get("/", tags=["Health"])
def root_endpoint():
    """Root endpoint welcoming visitors and linking to interactive docs."""
    return {
        "message": f"Welcome to {settings.APP_NAME} Adaptive Fitness API",
        "documentation": "/docs",
        "health": "/health"
    }
