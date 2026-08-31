import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from app.config import Settings


def test_settings__rejects_a_key_that_is_not_a_fernet_key() -> None:
    with pytest.raises(ValidationError):
        Settings(matrix_token_encryption_key="replace-with-a-fernet-key")


def test_settings__treats_a_blank_key_as_unset() -> None:
    assert Settings(matrix_token_encryption_key="").matrix_token_encryption_key is None


def test_settings__matrix_is_configured_only_when_every_part_is_present() -> None:
    key = Fernet.generate_key().decode("utf-8")

    assert not Settings().matrix_login_configured
    assert not Settings(matrix_oidc_client_id="client").matrix_login_configured
    assert not Settings(
        matrix_oidc_client_id="client",
        matrix_homeserver_url="https://matrix.example.com",
    ).matrix_login_configured

    configured = Settings(
        matrix_oidc_client_id="client",
        matrix_homeserver_url="https://matrix.example.com",
        matrix_token_encryption_key=key,
    )
    assert configured.matrix_login_configured
    assert configured.matrix_media_configured
