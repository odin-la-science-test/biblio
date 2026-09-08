"""
Configuration settings for the OLS Bibliography backend.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "OLS Bibliography"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ols_bibliography.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys (for external sources)
    PUBMED_API_KEY: str | None = None
    OPENALEX_API_URL: str = "https://api.openalex.org"
    CROSSREF_API_URL: str = "https://api.crossref.org"
    SEMANTIC_SCHOLAR_API_URL: str = "https://api.semanticscholar.org"
    
    # Search settings
    MAX_RESULTS_PER_SOURCE: int = 50
    SEARCH_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
