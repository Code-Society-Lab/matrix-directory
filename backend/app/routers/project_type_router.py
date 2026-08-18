from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.project_type import ProjectType
from app.schemas.project_type import ProjectTypeRead
from app.services import project_types_service

router = APIRouter(prefix="/project-types", tags=["project types"])


@router.get("/", response_model=list[ProjectTypeRead])
def list_project_types(
    session: Session = Depends(get_session),
) -> list[ProjectType]:
    return project_types_service.list_project_types(session)
