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
    demo_bootstrap_on_start: bool = False
    # Stable demo identity used only in DEMO_MODE so a full dataset reset cannot
    # temporarily delete the bearer identity that the UI is using.
    demo_master_token: str = ""
    seed: int = 42
    evidence_storage_dir: str = "./storage/evidence"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:5173"
    auth_provider_domain: str = ""
    auth_provider_audience: str = ""

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_account_number: str = ""
    razorpay_merchant_id: str = ""
    razorpay_webhook_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
