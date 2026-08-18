from sqlmodel import Session, select

from app.models.profile import Profile
from app.models.label import Label
from app.models.project_type import ProjectType
from app.models.user import User
from app.seed import (
    PROJECT_TYPE_NAMES,
    get_or_create_label,
    get_or_create_profile,
    get_or_create_project_type,
    get_or_create_user,
)


def test_project_type_names__expect_supported_taxonomy() -> None:
    assert PROJECT_TYPE_NAMES == (
        "Bot",
        "SDK",
        "Framework",
        "Bridges",
        "Clients",
        "Server",
        "Integrations",
    )


def test_seed_with_migrated_profile__expect_existing_user_reused(
    session: Session,
) -> None:
    legacy_user = User(
        oidc_issuer="legacy-issuer",
        oidc_subject="legacy-subject",
    )
    session.add(legacy_user)
    session.flush()
    session.add(
        Profile(
            user_id=legacy_user.id,
            matrix_id="@owner:example.org",
        )
    )
    session.commit()

    owner = get_or_create_user(
        session,
        oidc_issuer="seed-issuer",
        oidc_subject="seed-subject",
        matrix_id="@owner:example.org",
    )
    profile = get_or_create_profile(
        session,
        user=owner,
        matrix_id="@owner:example.org",
        display_name="Owner",
    )
    session.commit()

    assert owner.id == legacy_user.id
    assert profile.user_id == legacy_user.id
    assert len(session.exec(select(User)).all()) == 1
    assert len(session.exec(select(Profile)).all()) == 1


def test_seed_without_profile__expect_user_created(session: Session) -> None:
    owner = get_or_create_user(
        session,
        oidc_issuer="seed-issuer",
        oidc_subject="seed-subject",
        matrix_id="@owner:example.org",
    )

    assert owner.oidc_issuer == "seed-issuer"
    assert owner.oidc_subject == "seed-subject"


def test_seed_classifications__expect_existing_values_reused(session: Session) -> None:
    project_type = get_or_create_project_type(session, name="Bot")
    label = get_or_create_label(session, name="Utility")

    assert get_or_create_project_type(session, name="Bot").id == project_type.id
    assert get_or_create_label(session, name="Utility").id == label.id
    assert len(session.exec(select(ProjectType)).all()) == 1
    assert len(session.exec(select(Label)).all()) == 1
