from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./network_monitor.db"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    DEFAULT_PING_INTERVAL_SECONDS: int = 60
    MIN_PING_INTERVAL_SECONDS: int = 10
    MAX_PING_INTERVAL_SECONDS: int = 3600
    HISTORY_RETENTION_HOURS: int = 24
    PING_TIMEOUT_SECONDS: float = 2.0
    SLACK_WEBHOOK_URL: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
