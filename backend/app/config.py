"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+psycopg://todouser:todopass@localhost:5432/tododb"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600
    db_pool_pre_ping: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    
    # Redis (optional - will work without Redis if not configured)
    redis_url: str | None = None
    redis_enabled: bool = False
    cache_ttl: int = 600
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_ai_parse: str = "10/minute"
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
