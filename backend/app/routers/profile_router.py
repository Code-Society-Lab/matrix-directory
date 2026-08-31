from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from starlette.background import BackgroundTask

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
from app.services import matrix_avatar, project_queries
from app.services.errors import (
    MatrixAvatarConfigurationError,
    MatrixAvatarUnavailableError,
)

from ..utils.datetime import utc_now

router = APIRouter(prefix="/profile", tags=["profile"])
public_router = APIRouter(prefix="/profiles", tags=["profiles"])


@public_router.get("/{user_id}/avatar")
async def get_public_avatar(
    user_id: UUID,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Stream a Matrix avatar using server-side OAuth credentials."""
    try:
        media = await matrix_avatar.open_avatar_stream(session, user_id=user_id)
    except MatrixAvatarConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Matrix media proxying is not configured",
        ) from exc
    except MatrixAvatarUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        ) from exc

    return StreamingResponse(
        media.iter_bytes(),
        media_type=media.media_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            # These bytes come from a Matrix user and are served from this
            # application's own origin, so never let a browser re-sniff them.
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; sandbox",
        },
        background=BackgroundTask(media.close),
    )


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


@router.delete("/me/matrix-avatar", response_model=ProfileRead)
def disconnect_my_matrix_avatar(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Profile:
    """Stop using the Matrix avatar and delete the stored Matrix credential."""
    profile = _get_profile_or_404(session, user.id)

    matrix_avatar.disconnect_matrix_avatar(session, user_id=user.id)
    session.refresh(profile)

    return profile
