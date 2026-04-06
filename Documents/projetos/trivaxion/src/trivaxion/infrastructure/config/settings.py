from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Trivaxion"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/trivaxion"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    elasticsearch_url: str = Field(default="http://localhost:9200")
    elasticsearch_index_prefix: str = "trivaxion"

    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480  # 8 hours
    jwt_refresh_token_expire_days: int = 7

    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    log_level: str = "INFO"
    log_format: str = "json"

    scraper_timeout_seconds: int = 30
    scraper_max_retries: int = 3
    scraper_retry_delay_seconds: int = 2

    receita_federal_base_url: str = "https://www.receitafederal.gov.br"
    certidao_trabalhista_url: str = "https://www.tst.jus.br/certidao1"

    max_analyses_per_month_free: int = 100
    max_analyses_per_month_starter: int = 500
    max_analyses_per_month_professional: int = 2000
    max_analyses_per_month_enterprise: int = 99999

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
