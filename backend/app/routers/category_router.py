from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.category import Category
from app.schemas.category import CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    session: Session = Depends(get_session),
) -> list[Category]:
    return list(session.exec(select(Category).order_by(Category.name)).all())
