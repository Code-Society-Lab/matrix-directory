from uuid import UUID

from sqlmodel import Session, select

from app.models.project_type import ProjectType

from .errors import ProjectTypeNotFoundError


def list_project_types(session: Session) -> list[ProjectType]:
    statement = select(ProjectType).order_by(ProjectType.name)
    return list(session.exec(statement).all())


def get_project_type(session: Session, project_type_id: UUID) -> ProjectType:
    project_type = session.get(ProjectType, project_type_id)
    if project_type is None:
        raise ProjectTypeNotFoundError(f"Project type not found: {project_type_id}")

    return project_type
