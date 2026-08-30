from functools import lru_cache

from cryptography.fernet import Fernet
from pydantic import field_validator
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
    matrix_homeserver_url: str | None = None
    matrix_oidc_scope: str = "openid urn:matrix:client:api:*"
    matrix_token_encryption_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("matrix_token_encryption_key", mode="before")
    @classmethod
    def validate_encryption_key(cls, value: object) -> object:
        """Reject an unusable Fernet key at startup instead of at login."""
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValueError("MATRIX_TOKEN_ENCRYPTION_KEY must be a string")

        try:
            Fernet(value.encode("utf-8"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "MATRIX_TOKEN_ENCRYPTION_KEY must be a Fernet key. Generate one with: "
                'python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            ) from exc

        return value

    @property
    def matrix_media_configured(self) -> bool:
        """Whether the backend can proxy Matrix media for a stored credential."""
        return bool(self.matrix_homeserver_url and self.matrix_token_encryption_key)

    @property
    def matrix_login_configured(self) -> bool:
        """Whether Matrix login can run end to end, including avatar storage."""
        return bool(self.matrix_oidc_client_id) and self.matrix_media_configured


@lru_cache
def get_settings() -> Settings:
    return Settings()
