"""
Application configuration using pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "E-Auction API"
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eauction"
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    jwt_secret_key: str = "dev-secret-key-do-not-use-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 1 day

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]
        
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
