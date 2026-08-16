from sqlmodel import Session, select

from app.database import engine
from app.models.category import Category
from app.models.profile import Profile
from app.models.project import Project
from app.models.user import User

ADA_REPOSITORY_URL = "https://github.com/Code-Society-Lab/ada"

SEED_OIDC_ISSUER = "seed://matrix-directory"
SEED_OIDC_SUBJECT = "penguinboi"
SEED_MATRIX_ID = "@penguinboi:matrix.org"


def get_or_create_user(
    session: Session,
    *,
    oidc_issuer: str,
    oidc_subject: str,
    matrix_id: str | None = None,
) -> User:
    user = session.exec(
        select(User).where(
            User.oidc_issuer == oidc_issuer,
            User.oidc_subject == oidc_subject,
        )
    ).first()

    if user is not None:
        return user

    # Profiles created by the profile migration belong to the original user,
    # whose OIDC fields may still be null. Reuse that user instead of creating
    # a second account that would collide with the unique Matrix ID.
    if matrix_id is not None:
        profile = session.exec(
            select(Profile).where(Profile.matrix_id == matrix_id)
        ).first()

        if profile is not None:
            existing_user = session.get(User, profile.user_id)
            if existing_user is not None:
                return existing_user

    user = User(
        oidc_issuer=oidc_issuer,
        oidc_subject=oidc_subject,
    )

    session.add(user)
    session.flush()

    return user


def get_or_create_profile(
    session: Session,
    *,
    user: User,
    matrix_id: str,
    display_name: str | None = None,
) -> Profile:
    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()

    if profile:
        profile.matrix_id = matrix_id
        profile.display_name = display_name

        return profile

    profile = Profile(
        user_id=user.id,
        matrix_id=matrix_id,
        display_name=display_name,
    )

    session.add(profile)
    session.flush()

    return profile


def get_or_create_category(
    session: Session,
    *,
    name: str,
) -> Category:
    category = session.exec(select(Category).where(Category.name == name)).first()

    if category is not None:
        return category

    category = Category(name=name)

    session.add(category)
    session.flush()

    return category


def get_or_create_ada(
    session: Session,
    *,
    owner: User,
    categories: list[Category],
) -> Project:
    project = session.exec(
        select(Project).where(Project.repository_url == ADA_REPOSITORY_URL)
    ).first()

    if project is None:
        project = Project(
            name="Ada",
            short_description="",
            description="",
            repository_url=ADA_REPOSITORY_URL,
            user_id=owner.id,
        )

        session.add(project)

    project.name = "Ada"
    project.short_description = (
        "Code Society Lab's general-purpose Matrix bot built with matrix.py."
    )
    project.description = (
        "Ada is an open-source Matrix bot maintained by Code Society Lab. "
        "It provides a growing collection of Matrix room utilities and "
        "serves as a real-world consumer of the matrix.py framework."
    )
    project.user_id = owner.id
    project.website_url = "https://codesociety.xyz/"
    project.matrix_server_url = "https://matrix.to/#/#codesociety:matrix.org"
    project.supports_e2ee = False
    project.categories = categories

    return project


def seed() -> None:
    with Session(engine) as session:
        owner = get_or_create_user(
            session,
            oidc_issuer=SEED_OIDC_ISSUER,
            oidc_subject=SEED_OIDC_SUBJECT,
            matrix_id=SEED_MATRIX_ID,
        )

        get_or_create_profile(
            session,
            user=owner,
            matrix_id=SEED_MATRIX_ID,
            display_name="PenguinBoi",
        )

        development_category = get_or_create_category(
            session,
            name="Dev tools",
        )

        utilities_category = get_or_create_category(
            session,
            name="Utility",
        )

        get_or_create_ada(
            session,
            owner=owner,
            categories=[
                development_category,
                utilities_category,
            ],
        )

        session.commit()


if __name__ == "__main__":
    seed()
