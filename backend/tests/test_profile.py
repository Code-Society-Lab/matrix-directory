from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.profile import Profile
from app.models.user import User
from app.routers.profile_router import update_my_profile
from app.schemas.auth import CurrentUserRead
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserRead


def make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def profile_update(matrix_id: str) -> ProfileUpdate:
    return ProfileUpdate(
        matrix_id=matrix_id,
        display_name="Owner",
        bio=None,
        avatar_url=None,
        github_url=None,
        website_url=None,
    )


def test_changing_matrix_id_clears_verification() -> None:
    with make_session() as session:
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


def test_unchanged_matrix_id_keeps_verification() -> None:
    with make_session() as session:
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


def test_user_schemas_serialize_profile_relationships() -> None:
    with make_session() as session:
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
