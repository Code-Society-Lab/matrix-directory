from uuid import UUID

from sqlmodel import Session, select

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.datetime import utc_now

from . import labels_service, project_types_service
from .errors import ProjectLinkRequiredError


def create_project(
    session: Session,
    data: ProjectCreate,
    *,
    user_id: UUID,
) -> Project:
    project_type = project_types_service.get_project_type(session, data.project_type_id)
    labels = labels_service.get_labels(session, data.label_ids)
    project_data = data.model_dump(exclude={"project_type_id", "label_ids"})

    project = Project(
        **project_data,
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
    _validate_project_link(project, update_data)

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

    project.updated_at = utc_now()
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


def _validate_project_link(project: Project, update_data: dict[str, object]) -> None:
    repository_url = update_data.get("repository_url", project.repository_url)
    website_url = update_data.get("website_url", project.website_url)
    if repository_url is None and website_url is None:
        raise ProjectLinkRequiredError(
            "Provide at least a repository URL or website URL"
        )


def _get_owned_project(
    session: Session,
    project_id: UUID,
    user_id: UUID,
) -> Project | None:
    statement = select(Project).where(
        Project.id == project_id,
        Project.user_id == user_id,
    )
    return session.exec(statement).first()
