from sqlmodel import Session, select

from app.database import engine
from app.models.label import Label
from app.models.profile import Profile
from app.models.project import Project
from app.models.project_type import ProjectType
from app.models.user import User

ADA_REPOSITORY_URL = "https://github.com/Code-Society-Lab/ada"

PROJECT_TYPE_NAMES = (
    "Bot",
    "SDK",
    "Framework",
    "Bridges",
    "Clients",
    "Server",
    "Integrations",
)

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


def get_or_create_project_type(
    session: Session,
    *,
    name: str,
) -> ProjectType:
    project_type = session.exec(
        select(ProjectType).where(ProjectType.name == name)
    ).first()

    if project_type is not None:
        return project_type

    project_type = ProjectType(name=name)

    session.add(project_type)
    session.flush()

    return project_type


def get_or_create_label(
    session: Session,
    *,
    name: str,
) -> Label:
    label = session.exec(select(Label).where(Label.name == name)).first()

    if label is not None:
        return label

    label = Label(name=name)

    session.add(label)
    session.flush()

    return label


def get_or_create_ada(
    session: Session,
    *,
    owner: User,
    project_type: ProjectType,
    labels: list[Label],
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
            project_type_id=project_type.id,
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
    project.project_type = project_type
    project.labels = labels

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

        project_types = {
            name: get_or_create_project_type(session, name=name)
            for name in PROJECT_TYPE_NAMES
        }

        development_label = get_or_create_label(
            session,
            name="Dev tools",
        )

        utilities_label = get_or_create_label(
            session,
            name="Utility",
        )

        get_or_create_ada(
            session,
            owner=owner,
            project_type=project_types["Bot"],
            labels=[
                development_label,
                utilities_label,
            ],
        )

        session.commit()


if __name__ == "__main__":
    seed()
