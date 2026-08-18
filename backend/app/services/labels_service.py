from typing import Any, cast
from uuid import UUID

from sqlmodel import Session, select

from app.models.label import Label

from .errors import LabelNotFoundError


def list_labels(session: Session) -> list[Label]:
    statement = select(Label).order_by(Label.name)
    return list(session.exec(statement).all())


def get_labels(session: Session, label_ids: list[UUID]) -> list[Label]:
    if not label_ids:
        return []

    label_id_column = cast(Any, Label.id)
    statement = select(Label).where(label_id_column.in_(label_ids))
    labels = list(session.exec(statement).all())

    found_ids = {label.id for label in labels}
    missing_ids = set(label_ids) - found_ids
    if missing_ids:
        raise LabelNotFoundError(f"Labels not found: {missing_ids}")

    return labels
