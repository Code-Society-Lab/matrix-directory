from typing import Any, cast

from sqlmodel import Session, select
from uuid import UUID

from app.models.category import Category
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

from .errors import CategoryNotFoundError, ProjectLinkRequiredError


def list_projects(session: Session) -> list[Project]:
    statement = select(Project)
    return list(session.exec(statement).all())


def list_projects_for_user(session: Session, *, user_id: UUID) -> list[Project]:
    statement = select(Project).where(Project.user_id == user_id)
    return list(session.exec(statement).all())


def get_project(
    session: Session,
    project_id: UUID,
) -> Project | None:
    return session.get(Project, project_id)


def create_project(
    session: Session,
    data: ProjectCreate,
    *,
    user_id: UUID,
) -> Project:
    if not data.category_ids:
        raise ValueError("A project must have at least one category")

    categories = _get_categories(session, data.category_ids)

    project = Project(
        name=data.name,
        description=data.description,
        short_description=data.short_description,
        repository_url=data.repository_url,
        website_url=data.website_url,
        matrix_server_url=data.matrix_server_url,
        supports_e2ee=data.supports_e2ee,
        user_id=user_id,
        categories=categories,
    )

    session.add(project)
    session.commit()
    session.refresh(project)

    return project


def update_project(
    session: Session,
    project_id: UUID,
    data: ProjectUpdate,
    *,
    user_id: UUID,
) -> Project | None:
    project = _get_owned_project(session, project_id, user_id)

    if project is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"category_ids"},
    )

    repository_url = update_data.get("repository_url", project.repository_url)
    website_url = update_data.get("website_url", project.website_url)
    if repository_url is None and website_url is None:
        raise ProjectLinkRequiredError(
            "Provide at least a repository URL or website URL"
        )

    for field, value in update_data.items():
        setattr(project, field, value)

    if data.category_ids is not None:
        if not data.category_ids:
            raise ValueError("A project must have at least one category")

        project.categories = _get_categories(
            session,
            data.category_ids,
        )

    session.add(project)
    session.commit()
    session.refresh(project)

    return project


def delete_project(
    session: Session,
    project_id: UUID,
    *,
    user_id: UUID,
) -> bool:
    project = _get_owned_project(session, project_id, user_id)

    if project is None:
        return False

    session.delete(project)
    session.commit()

    return True


def _get_owned_project(
    session: Session, project_id: UUID, user_id: UUID
) -> Project | None:
    return session.exec(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    ).first()


def _get_categories(
    session: Session,
    category_ids: list[UUID],
) -> list[Category]:
    category_id_column = cast(Any, Category.id)
    statement = select(Category).where(category_id_column.in_(category_ids))

    categories = list(session.exec(statement).all())

    if len(categories) != len(set(category_ids)):
        found_ids = {category.id for category in categories}
        missing_ids = set(category_ids) - found_ids

        raise CategoryNotFoundError(f"Categories not found: {missing_ids}")

    return categories
