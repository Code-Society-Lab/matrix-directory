from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.models.label import Label
from app.models.profile import Profile
from app.models.project import Project
from app.models.project_label import ProjectLabel
from app.models.project_type import ProjectType
from app.models.user import User

_PROJECT_LOAD_OPTIONS = (
    selectinload(cast(Any, Project.project_type)),
    selectinload(cast(Any, Project.labels)),
    selectinload(cast(Any, Project.owner)).selectinload(cast(Any, User.profile)),
)


def list_projects(
    session: Session,
    *,
    query: str | None = None,
    project_type: str | None = None,
    label: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Project]:
    filters = _build_filters(
        query=query,
        project_type=project_type,
        label=label,
    )
    statement = (
        select(Project)
        .where(*filters)
        .options(*_PROJECT_LOAD_OPTIONS)
        .order_by(col(Project.created_at).desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def count_projects(
    session: Session,
    *,
    query: str | None = None,
    project_type: str | None = None,
    label: str | None = None,
) -> int:
    filters = _build_filters(
        query=query,
        project_type=project_type,
        label=label,
    )
    statement = select(func.count()).select_from(Project).where(*filters)
    return int(session.exec(statement).one())


def list_random_projects(
    session: Session,
    *,
    limit: int = 6,
) -> list[Project]:
    statement = (
        select(Project)
        .options(*_PROJECT_LOAD_OPTIONS)
        .order_by(func.random())
        .limit(limit)
    )
    return list(session.exec(statement).all())


def list_projects_for_user(session: Session, *, user_id: UUID) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.user_id == user_id)
        .options(*_PROJECT_LOAD_OPTIONS)
        .order_by(
            col(Project.updated_at).desc(),
            col(Project.created_at).desc(),
        )
    )
    return list(session.exec(statement).all())


def get_project(
    session: Session,
    project_id: UUID,
) -> Project | None:
    statement = (
        select(Project).where(Project.id == project_id).options(*_PROJECT_LOAD_OPTIONS)
    )
    return session.exec(statement).first()


def _build_filters(
    *,
    query: str | None,
    project_type: str | None,
    label: str | None,
) -> list[Any]:
    filters: list[Any] = []
    normalized_query = query.strip() if query else ""

    if normalized_query:
        pattern = _literal_contains_pattern(normalized_query)
        matching_project_types = select(ProjectType.id).where(
            col(ProjectType.name).ilike(pattern, escape="\\")
        )
        matching_project_labels = (
            select(ProjectLabel.project_id)
            .join(Label, col(ProjectLabel.label_id) == col(Label.id))
            .where(col(Label.name).ilike(pattern, escape="\\"))
        )
        matching_owners = select(Profile.user_id).where(
            or_(
                col(Profile.display_name).ilike(pattern, escape="\\"),
                col(Profile.matrix_id).ilike(pattern, escape="\\"),
            )
        )
        filters.append(
            or_(
                col(Project.name).ilike(pattern, escape="\\"),
                col(Project.short_description).ilike(pattern, escape="\\"),
                col(Project.description).ilike(pattern, escape="\\"),
                col(Project.project_type_id).in_(matching_project_types),
                col(Project.id).in_(matching_project_labels),
                col(Project.user_id).in_(matching_owners),
            )
        )

    if project_type:
        matching_project_type = select(ProjectType.id).where(
            ProjectType.name == project_type
        )
        filters.append(col(Project.project_type_id).in_(matching_project_type))

    if label:
        matching_label = (
            select(ProjectLabel.project_id)
            .join(Label, col(ProjectLabel.label_id) == col(Label.id))
            .where(col(Label.name) == label)
        )
        filters.append(col(Project.id).in_(matching_label))

    return filters


def _literal_contains_pattern(value: str) -> str:
    escaped_value = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped_value}%"
