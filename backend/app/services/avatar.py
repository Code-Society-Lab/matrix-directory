"""Single source of truth for how a profile's avatar is addressed publicly."""

from uuid import UUID

from app.models.profile import Profile


def matrix_avatar_path(user_id: UUID) -> str:
    """Return the local proxy path that serves a user's Matrix avatar."""
    return f"/api/profiles/{user_id}/avatar"


def matrix_avatar_url(profile: Profile) -> str | None:
    """Return the proxy URL when the profile has a Matrix avatar to serve."""
    if profile.matrix_avatar_mxc is None:
        return None

    return matrix_avatar_path(profile.user_id)


def resolve_avatar_url(profile: Profile) -> str | None:
    """Return the avatar a visitor should load, preferring an explicit choice.

    A custom URL always wins. The Matrix avatar is the fallback so that signing
    in yields a usable avatar without the proxy path ever being stored.
    """
    if profile.avatar_url:
        return profile.avatar_url

    return matrix_avatar_url(profile)
