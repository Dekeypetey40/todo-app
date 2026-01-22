"""
FastAPI main application.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from .routers import tasks, projects, tags, ai
from .config import settings
from .exceptions import AppException, ResourceAlreadyExistsError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# DO NOT use Base.metadata.create_all() here!
# Database migrations should be handled by Alembic exclusively.
# Run 'alembic upgrade head' to apply migrations.

app = FastAPI(
    title="Todo API",
    description="A full-featured todo application API with projects, tags, and smart views",
    version="1.0.0",
    debug=settings.debug
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, enabled=settings.rate_limit_enabled)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with environment-based configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(ai.router)


# Global Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle custom application exceptions.
    """
    logger.warning(f"Application exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers or {}
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors (unique constraints, foreign keys, etc.).
    """
    logger.error(f"Database integrity error: {exc}", exc_info=True)
    
    # Parse the error to provide user-friendly messages
    error_msg = str(exc.orig)
    if "unique constraint" in error_msg.lower():
        detail = "A resource with this value already exists"
    elif "foreign key constraint" in error_msg.lower():
        detail = "Referenced resource does not exist"
    else:
        detail = "Database constraint violation"
    
    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Catch SQLAlchemy errors and return proper JSON response.
    """
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred. Please try again later."}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and return proper error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # In development, show the actual error. In production, hide details.
    error_detail = str(exc) if settings.debug else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail}
    )


@app.get("/")
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Todo API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Comprehensive health check endpoint.
    Checks database connectivity and external service availability.
    """
    from .database import check_database_connection
    import os
    
    health_status = {
        "status": "healthy",
        "environment": settings.environment,
        "checks": {
            "database": "unknown",
            "ai_service": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        if check_database_connection():
            health_status["checks"]["database"] = "healthy"
        else:
            health_status["checks"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Health check - database error: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check AI service configuration
    if settings.openai_api_key and settings.openai_api_key != "your-api-key-here":
        health_status["checks"]["ai_service"] = "configured"
    else:
        health_status["checks"]["ai_service"] = "not_configured"
    
    # Check Redis (optional)
    if settings.redis_enabled and settings.redis_url:
        try:
            from redis import Redis
            r = Redis.from_url(settings.redis_url)
            r.ping()
            health_status["checks"]["redis"] = "healthy"
        except Exception as e:
            logger.error(f"Health check - Redis error: {e}")
            health_status["checks"]["redis"] = "unhealthy"
    else:
        health_status["checks"]["redis"] = "not_configured"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
