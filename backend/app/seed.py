from sqlmodel import Session, select

from app.database import engine
from app.models.category import Category
from app.models.project import Project
from app.models.user import User

ADA_REPOSITORY_URL = "https://github.com/Code-Society-Lab/ada"


def get_or_create_user(
    session: Session,
    *,
    matrix_id: str,
) -> User:
    user = session.exec(select(User).where(User.matrix_id == matrix_id)).first()

    if user is not None:
        return user

    user = User(
        matrix_id=matrix_id,
    )

    session.add(user)
    session.flush()

    return user


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
            matrix_id="@penguinboi:matrix.org",
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
