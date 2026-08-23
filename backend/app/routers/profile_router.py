from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.models.profile import Profile
from app.models.user import User
from app.schemas.project import ProjectRead
from app.schemas.profile import (
    ProfileRead,
    ProfileUpdate,
    PublicProfileRead,
    ProfilePublicFields,
)
from app.services import project_queries

from ..utils.datetime import utc_now

router = APIRouter(prefix="/profile", tags=["profile"])
public_router = APIRouter(prefix="/profiles", tags=["profiles"])


def _get_profile_or_404(
    session: Session,
    user_id: UUID,
) -> Profile:
    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@public_router.get("/{user_id}", response_model=PublicProfileRead)
def get_public_profile(
    user_id: UUID,
    session: Session = Depends(get_session),
) -> PublicProfileRead:
    profile = _get_profile_or_404(session, user_id)

    profile_fields = ProfilePublicFields.model_validate(profile)

    projects = [
        ProjectRead.model_validate(project)
        for project in project_queries.list_projects_for_user(
            session,
            user_id=user_id,
        )
    ]

    return PublicProfileRead(
        user_id=user_id,
        projects=projects,
        **profile_fields.model_dump(),
    )


@router.put("/me", response_model=ProfileRead)
def update_my_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Profile:
    profile = _get_profile_or_404(session, user.id)

    for field, value in data.model_dump().items():
        setattr(profile, field, value)

    profile.updated_at = utc_now()

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile
