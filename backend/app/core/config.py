"""
Central configuration. Everything that varies between a laptop demo run and a
production deployment lives here, read once from the environment.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./first_hour.db"
    demo_mode: bool = True
    seed: int = 42
    evidence_storage_dir: str = "./storage/evidence"
    anthropic_api_key: str = ""
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
