import pytest
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlmodel import Session
from uuid import uuid4

from app.models.profile import Profile
from app.models.project import Project
from app.models.project_type import ProjectType
from app.models.user import User
from app.routers.profile_router import get_public_profile, update_my_profile
from app.schemas.auth import CurrentUserRead
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserRead


def profile_update() -> ProfileUpdate:
    return ProfileUpdate(
        display_name="Owner",
        bio=None,
        avatar_url=None,
        github_url=None,
        website_url=None,
    )


def test_profile_update__preserves_server_managed_matrix_identity(
    session: Session,
) -> None:
    user = User(oidc_issuer="issuer", oidc_subject="subject")
    session.add(user)
    session.flush()
    session.add(
        Profile(
            user_id=user.id,
            matrix_id="@old:example.org",
            matrix_id_verified=True,
        )
    )
    session.commit()

    profile = update_my_profile(
        profile_update(),
        user,
        session,
    )

    assert profile.matrix_id == "@old:example.org"
    assert profile.matrix_id_verified is True


def test_profile_update__rejects_matrix_id() -> None:
    with pytest.raises(ValidationError):
        ProfileUpdate.model_validate(
            {
                "matrix_id": "@other:example.org",
                "display_name": "Owner",
            }
        )


def test_profile_update__returns_404_when_profile_is_missing(
    session: Session,
) -> None:
    user = User(oidc_issuer="issuer", oidc_subject="subject")
    session.add(user)
    session.commit()

    with pytest.raises(HTTPException) as exc_info:
        update_my_profile(profile_update(), user, session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Profile not found"


def test_public_profile__returns_404_when_profile_is_missing(
    session: Session,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_public_profile(uuid4(), session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Profile not found"


def test_user_schemas__expect_profile_relationships_serialized(
    session: Session,
) -> None:
    user = User(oidc_issuer="issuer", oidc_subject="subject")
    session.add(user)
    session.flush()
    profile = Profile(
        user_id=user.id,
        matrix_id="@owner:example.org",
    )
    session.add(profile)
    session.commit()

    current_user = CurrentUserRead.model_validate(user)
    user_read = UserRead.model_validate(user)

    assert current_user.profile is not None
    assert current_user.profile.id == profile.id
    assert current_user.profile.matrix_id == "@owner:example.org"
    assert user_read.profile == current_user.profile
    assert user_read.project_ids == []


def test_public_profile__exposes_profile_and_owned_projects_without_oidc_fields(
    session: Session,
) -> None:
    user = User(oidc_issuer="private-issuer", oidc_subject="private-subject")
    project_type = ProjectType(name="Bot")
    session.add_all([user, project_type])
    session.flush()
    session.add(
        Profile(
            user_id=user.id,
            matrix_id="@owner:example.org",
            matrix_id_verified=True,
            display_name="Owner",
            bio="Maintains Matrix projects.",
            github_url="https://github.com/owner",
            website_url="https://example.org",
        )
    )
    session.add(
        Project(
            name="Owner bot",
            short_description="A bot maintained by this profile.",
            description="About this bot.",
            repository_url="https://github.com/owner/bot",
            user_id=user.id,
            project_type_id=project_type.id,
        )
    )
    session.commit()

    public_profile = get_public_profile(user.id, session)

    assert public_profile.display_name == "Owner"
    assert public_profile.matrix_id_verified is True
    assert [project.name for project in public_profile.projects] == ["Owner bot"]
    assert "oidc_issuer" not in public_profile.model_dump()
    assert "oidc_subject" not in public_profile.model_dump()
