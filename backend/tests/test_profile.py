from sqlmodel import Session

from app.models.profile import Profile
from app.models.project import Project
from app.models.project_type import ProjectType
from app.models.user import User
from app.routers.profile_router import get_public_profile, update_my_profile
from app.schemas.auth import CurrentUserRead
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserRead


def profile_update(matrix_id: str) -> ProfileUpdate:
    return ProfileUpdate(
        matrix_id=matrix_id,
        display_name="Owner",
        bio=None,
        avatar_url=None,
        github_url=None,
        website_url=None,
    )


def test_changing_matrix_id__expect_verification_cleared(session: Session) -> None:
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
        profile_update("@new:example.org"),
        user,
        session,
    )

    assert profile.matrix_id == "@new:example.org"
    assert profile.matrix_id_verified is False


def test_unchanged_matrix_id__expect_verification_preserved(session: Session) -> None:
    user = User(oidc_issuer="issuer", oidc_subject="subject")
    session.add(user)
    session.flush()
    session.add(
        Profile(
            user_id=user.id,
            matrix_id="@owner:example.org",
            matrix_id_verified=True,
        )
    )
    session.commit()

    profile = update_my_profile(
        profile_update("@owner:example.org"),
        user,
        session,
    )

    assert profile.matrix_id_verified is True


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
