from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.category import Category
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectUpdate
from app.services.projects_service import delete_project, update_project


def test_project_writes_are_limited_to_owner() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        owner = User(oidc_issuer="issuer", oidc_subject="owner")
        stranger = User(oidc_issuer="issuer", oidc_subject="stranger")
        category = Category(name="Bots")
        session.add_all([owner, stranger, category])
        session.flush()
        project = Project(
            name="Test Bot",
            description="Test bot",
            short_description="Test bot",
            user_id=owner.id,
            categories=[category],
        )
        session.add(project)
        session.commit()

        assert (
            update_project(
                session,
                project.id,
                ProjectUpdate(name="Hijacked"),
                user_id=stranger.id,
            )
            is None
        )
        assert not delete_project(session, project.id, user_id=stranger.id)
        assert session.get(Project, project.id) is not None

        assert delete_project(session, project.id, user_id=owner.id)
        assert session.get(Project, project.id) is None
