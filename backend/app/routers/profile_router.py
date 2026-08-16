from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.put("/me", response_model=ProfileRead)
def update_my_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Profile:
    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()

    if profile is None:
        profile = Profile(user_id=user.id)

    values = data.model_dump()

    if values["matrix_id"] != profile.matrix_id:
        profile.matrix_id_verified = False

    for field, value in values.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile
