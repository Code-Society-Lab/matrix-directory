from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Matrix Directory API"
    environment: str = "development"
    database_url: str = "sqlite:///./matrix_directory.db"
    frontend_origin: str = "http://localhost:5173"
    app_secret: str = "development-only-change-me"
    session_cookie_secure: bool = False
    matrix_oidc_issuer: str = "https://account.matrix.org/"
    matrix_oidc_client_id: str | None = None
    matrix_oidc_client_secret: str | None = None
    matrix_oidc_redirect_uri: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
