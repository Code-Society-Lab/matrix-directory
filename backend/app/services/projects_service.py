from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, col, select

from app.models.label import Label
from app.models.profile import Profile
from app.models.project import Project
from app.models.project_label import ProjectLabel
from app.models.project_type import ProjectType
from app.schemas.project import ProjectCreate, ProjectUpdate

from . import labels_service, project_types_service
from .errors import ProjectLinkRequiredError


def list_projects(
    session: Session,
    *,
    query: str | None = None,
    project_type: str | None = None,
    label: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Project]:
    statement = select(Project)

    if query:
        pattern = f"%{query.strip()}%"
        matching_project_types = select(ProjectType.id).where(
            col(ProjectType.name).ilike(pattern)
        )
        matching_project_labels = (
            select(ProjectLabel.project_id)
            .join(Label, col(ProjectLabel.label_id) == col(Label.id))
            .where(col(Label.name).ilike(pattern))
        )
        matching_owners = select(Profile.user_id).where(
            or_(
                col(Profile.display_name).ilike(pattern),
                col(Profile.matrix_id).ilike(pattern),
            )
        )
        statement = statement.where(
            or_(
                col(Project.name).ilike(pattern),
                col(Project.short_description).ilike(pattern),
                col(Project.description).ilike(pattern),
                col(Project.project_type_id).in_(matching_project_types),
                col(Project.id).in_(matching_project_labels),
                col(Project.user_id).in_(matching_owners),
            )
        )

    if project_type:
        matching_project_type = select(ProjectType.id).where(
            ProjectType.name == project_type
        )
        statement = statement.where(
            col(Project.project_type_id).in_(matching_project_type)
        )

    if label:
        matching_label = (
            select(ProjectLabel.project_id)
            .join(Label, col(ProjectLabel.label_id) == col(Label.id))
            .where(col(Label.name) == label)
        )
        statement = statement.where(col(Project.id).in_(matching_label))

    statement = (
        statement.order_by(col(Project.created_at).desc()).offset(offset).limit(limit)
    )
    return list(session.exec(statement).all())


def count_projects(session: Session) -> int:
    statement = select(func.count()).select_from(Project)
    return int(session.exec(statement).one())


def list_random_projects(
    session: Session,
    *,
    limit: int = 6,
) -> list[Project]:
    statement = select(Project).order_by(func.random()).limit(limit)
    return list(session.exec(statement).all())


def list_projects_for_user(session: Session, *, user_id: UUID) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.user_id == user_id)
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
    return session.get(Project, project_id)


def create_project(
    session: Session,
    data: ProjectCreate,
    *,
    user_id: UUID,
) -> Project:
    project_type = project_types_service.get_project_type(session, data.project_type_id)
    labels = labels_service.get_labels(session, data.label_ids)

    project = Project(
        name=data.name,
        description=data.description,
        short_description=data.short_description,
        repository_url=data.repository_url,
        website_url=data.website_url,
        matrix_server_url=data.matrix_server_url,
        supports_e2ee=data.supports_e2ee,
        user_id=user_id,
        project_type=project_type,
        labels=labels,
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
        exclude={"project_type_id", "label_ids"},
    )

    repository_url = update_data.get("repository_url", project.repository_url)
    website_url = update_data.get("website_url", project.website_url)
    if repository_url is None and website_url is None:
        raise ProjectLinkRequiredError(
            "Provide at least a repository URL or website URL"
        )

    project_type = None
    if data.project_type_id is not None:
        project_type = project_types_service.get_project_type(
            session, data.project_type_id
        )

    labels = None
    if data.label_ids is not None:
        labels = labels_service.get_labels(session, data.label_ids)

    for field, value in update_data.items():
        setattr(project, field, value)

    if project_type is not None:
        project.project_type = project_type

    if labels is not None:
        project.labels = labels

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
