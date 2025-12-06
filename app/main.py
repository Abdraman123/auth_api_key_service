from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db.session import engine, get_db
from app.api.v1.routes import auth, api_keys, protected
from app.schemas.common import HealthResponse

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Authentication and API Key Management System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(api_keys.router, prefix=settings.API_V1_PREFIX)
app.include_router(protected.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {
        "message": "Auth API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    """
    # Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        database=db_status
    )


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"🚀 {settings.PROJECT_NAME} starting up...")
    print(f"📝 API Documentation: http://localhost:8000/docs")
    print(f"💾 Database: {settings.DATABASE_URL.split('@')[-1]}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"👋 {settings.PROJECT_NAME} shutting down...")
    engine.dispose()