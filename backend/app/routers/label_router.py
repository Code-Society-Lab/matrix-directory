from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.label import Label
from app.schemas.label import LabelRead
from app.services import labels_service

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("/", response_model=list[LabelRead])
def list_labels(
    session: Session = Depends(get_session),
) -> list[Label]:
    return labels_service.list_labels(session)
