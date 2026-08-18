from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID

from app.database import get_session
from app.dependencies import get_current_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import projects_service

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    session: Session = Depends(get_session),
) -> list[Project]:
    return projects_service.list_projects(session)


@router.get("/mine/", response_model=list[ProjectRead])
def list_my_projects(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[Project]:
    return projects_service.list_projects_for_user(session, user_id=user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    session: Session = Depends(get_session),
) -> Project:
    project = projects_service.get_project(session, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Project:
    try:
        return projects_service.create_project(session, data, user_id=user.id)
    except projects_service.CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Project:
    try:
        project = projects_service.update_project(
            session,
            project_id,
            data,
            user_id=user.id,
        )
    except (
        projects_service.CategoryNotFoundError,
        projects_service.ProjectLinkRequiredError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> None:
    deleted = projects_service.delete_project(session, project_id, user_id=user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
