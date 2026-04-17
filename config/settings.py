"""
Application configuration management.
Supports environment-based configuration with validation.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Database
    database_url: str = "postgresql://localhost:5432/inflation_sentiment"
    database_pool_size: int = 10
    database_echo: bool = False
    
    # Twitter API (X)
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # News API
    news_api_key: Optional[str] = None
    
    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Sentiment Analysis
    sentiment_model: str = "ProsusAI/finbert"
    device: str = "cpu"
    
    # MCP Server
    mcp_host: str = "localhost"
    mcp_port: int = 8000
    mcp_secret_key: str = "change-me-in-production"
    
    # Scraping
    scrape_interval_hours: int = 6
    batch_size: int = 50
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
