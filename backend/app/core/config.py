from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "beacon-lens"
    app_env: str = "development"
    demo_mode: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "sqlite+aiosqlite:///./beacon_lens.db"

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production-min-32-chars", min_length=32)
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ComfyUI
    comfyui_url: str = "http://localhost:8188"
    comfyui_timeout: int = 300

    # LLM (optional)
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""

    # Keycloak / OIDC
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "beacon-lens"
    keycloak_client_id: str = "beacon-lens-frontend"
    keycloak_client_secret: str = ""
    keycloak_admin_user: str = "admin"
    keycloak_admin_password: str = "admin"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
