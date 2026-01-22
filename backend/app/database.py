"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Configure database engine with proper connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,  # Number of persistent connections
    max_overflow=settings.db_max_overflow,  # Max burst connections
    pool_pre_ping=settings.db_pool_pre_ping,  # Test connections before use
    pool_recycle=settings.db_pool_recycle,  # Recycle connections after 1 hour
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Add connection pool logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections in debug mode."""
    if settings.debug:
        logger.debug("Database connection established")

@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections in debug mode."""
    if settings.debug:
        logger.debug("Database connection closed")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Check if database is accessible.
    Returns True if connection successful, False otherwise.
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
