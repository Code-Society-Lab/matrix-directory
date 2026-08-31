from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectFilters,
    ProjectRead,
    ProjectUpdate,
)
from app.services import project_commands, project_queries
from app.services.errors import (
    LabelNotFoundError,
    ProjectLinkRequiredError,
    ProjectTypeNotFoundError,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    filters: Annotated[ProjectFilters, Depends()],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[Project]:
    return project_queries.list_projects(
        session,
        query=filters.q,
        project_type=filters.project_type,
        label=filters.label,
        limit=limit,
        offset=offset,
    )


@router.get("/mine/", response_model=list[ProjectRead])
def list_my_projects(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[Project]:
    return project_queries.list_projects_for_user(session, user_id=user.id)


@router.get("/count/", response_model=int)
def count_projects(
    filters: Annotated[ProjectFilters, Depends()],
    session: Session = Depends(get_session),
) -> int:
    return project_queries.count_projects(
        session,
        query=filters.q,
        project_type=filters.project_type,
        label=filters.label,
    )


@router.get("/random/", response_model=list[ProjectRead])
def list_random_projects(
    limit: int = Query(default=6, ge=1, le=24),
    session: Session = Depends(get_session),
) -> list[Project]:
    return project_queries.list_random_projects(
        session,
        limit=limit,
    )


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    session: Session = Depends(get_session),
) -> Project:
    project = project_queries.get_project(session, project_id)
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
        return project_commands.create_project(session, data, user_id=user.id)
    except (
        LabelNotFoundError,
        ProjectTypeNotFoundError,
    ) as exc:
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
        project = project_commands.update_project(
            session,
            project_id,
            data,
            user_id=user.id,
        )
    except (
        LabelNotFoundError,
        ProjectLinkRequiredError,
        ProjectTypeNotFoundError,
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
    deleted = project_commands.delete_project(session, project_id, user_id=user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
