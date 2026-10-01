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

    # Production OIDC settings. The backend validates the signed access token
    # itself. No client secret is accepted here because the browser is a public
    # OAuth client and must use Authorization Code + PKCE.
    auth_provider_domain: str = ""
    auth_provider_issuer: str = ""
    auth_provider_audience: str = ""
    auth_provider_jwks_url: str = ""

    max_evidence_bytes: int = 10 * 1024 * 1024

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_account_number: str = ""
    razorpay_merchant_id: str = ""
    razorpay_webhook_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def oidc_issuer(self) -> str:
        if self.auth_provider_issuer:
            return self.auth_provider_issuer.rstrip("/") + "/"
        if self.auth_provider_domain:
            return f"https://{self.auth_provider_domain.rstrip('/')}/"
        return ""

    @property
    def oidc_jwks_url(self) -> str:
        if self.auth_provider_jwks_url:
            return self.auth_provider_jwks_url
        if self.auth_provider_domain:
            return f"https://{self.auth_provider_domain.rstrip('/')}/.well-known/jwks.json"
        return ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
