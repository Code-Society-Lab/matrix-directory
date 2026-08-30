from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

from .errors import TokenEncryptionError


class TokenCipher:
    """Symmetric cipher for Matrix OAuth tokens held at rest."""

    def __init__(self, encryption_key: str) -> None:
        try:
            self._fernet = Fernet(encryption_key.encode("utf-8"))
        except (TypeError, ValueError) as exc:
            raise TokenEncryptionError("Invalid Matrix token encryption key") from exc

    def encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_token: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
        except (InvalidToken, TypeError, ValueError) as exc:
            raise TokenEncryptionError("Could not decrypt Matrix OAuth token") from exc


@lru_cache
def get_token_cipher() -> TokenCipher:
    """Return the deployment cipher, built once from the configured key."""
    encryption_key = get_settings().matrix_token_encryption_key
    if encryption_key is None:
        raise TokenEncryptionError("Matrix token encryption key is not configured")

    return TokenCipher(encryption_key)
