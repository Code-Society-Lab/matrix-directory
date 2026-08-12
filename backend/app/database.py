from collections.abc import Generator

from sqlmodel import Session, create_engine
from sqlmodel_toolkit import Model

from app.config import get_settings
from app import models  # noqa: F401  # Register all models before relationship setup.

settings = get_settings()
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(settings.database_url, echo=True, connect_args=connect_args)
Model.set_engine(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
