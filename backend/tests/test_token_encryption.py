import pytest
from cryptography.fernet import Fernet

from app.services.errors import TokenEncryptionError
from app.services.token_encryption import TokenCipher


def test_token_cipher__round_trips_refresh_token() -> None:
    cipher = TokenCipher(Fernet.generate_key().decode("utf-8"))

    encrypted = cipher.encrypt("refresh-token")

    assert encrypted != "refresh-token"
    assert cipher.decrypt(encrypted) == "refresh-token"


def test_token_cipher__rejects_an_invalid_key() -> None:
    with pytest.raises(TokenEncryptionError):
        TokenCipher("not-a-fernet-key")


def test_token_cipher__rejects_a_token_from_another_key() -> None:
    encrypted = TokenCipher(Fernet.generate_key().decode("utf-8")).encrypt("token")

    with pytest.raises(TokenEncryptionError):
        TokenCipher(Fernet.generate_key().decode("utf-8")).decrypt(encrypted)
