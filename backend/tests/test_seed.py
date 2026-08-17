from sqlmodel import Session, select

from app.models.profile import Profile
from app.models.user import User
from app.seed import get_or_create_profile, get_or_create_user


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
