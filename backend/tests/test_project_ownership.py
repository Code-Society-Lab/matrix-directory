from uuid import uuid4

import pytest
from sqlmodel import Session

from app.models.label import Label
from app.models.project import Project
from app.models.project_type import ProjectType
from app.models.user import User
from app.schemas.project import ProjectUpdate
from app.services.errors import ProjectLinkRequiredError, ProjectTypeNotFoundError
from app.services.projects_service import delete_project, update_project


def test_project_writes__expect_only_owner_allowed(session: Session) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    stranger = User(oidc_issuer="issuer", oidc_subject="stranger")
    project_type = ProjectType(name="Bot")
    label = Label(name="Utility")
    session.add_all([owner, stranger, project_type, label])
    session.flush()
    project = Project(
        name="Test Bot",
        description="Test bot",
        short_description="Test bot",
        user_id=owner.id,
        project_type_id=project_type.id,
        labels=[label],
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


def test_project_update__expect_at_least_one_project_link(session: Session) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    project_type = ProjectType(name="Bot")
    session.add_all([owner, project_type])
    session.flush()
    project = Project(
        name="Test Bot",
        description="Test bot",
        short_description="Test bot",
        repository_url="https://example.com/repository",
        user_id=owner.id,
        project_type_id=project_type.id,
    )
    session.add(project)
    session.commit()

    with pytest.raises(ProjectLinkRequiredError):
        update_project(
            session,
            project.id,
            ProjectUpdate(repository_url=None),
            user_id=owner.id,
        )

    session.refresh(project)
    assert project.repository_url == "https://example.com/repository"


def test_project_update__expect_type_changed_and_labels_cleared(
    session: Session,
) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    bot_type = ProjectType(name="Bot")
    sdk_type = ProjectType(name="SDK")
    label = Label(name="Dev tools")
    session.add_all([owner, bot_type, sdk_type, label])
    session.flush()
    project = Project(
        name="Test project",
        description="Test project",
        short_description="Test project",
        repository_url="https://example.com/repository",
        user_id=owner.id,
        project_type_id=bot_type.id,
        labels=[label],
    )
    session.add(project)
    session.commit()

    updated = update_project(
        session,
        project.id,
        ProjectUpdate(project_type_id=sdk_type.id, label_ids=[]),
        user_id=owner.id,
    )

    assert updated is not None
    assert updated.project_type.id == sdk_type.id
    assert updated.labels == []


def test_project_update_with_unknown_type__expect_no_partial_changes(
    session: Session,
) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    project_type = ProjectType(name="Bot")
    session.add_all([owner, project_type])
    session.flush()
    project = Project(
        name="Original name",
        description="Test project",
        short_description="Test project",
        repository_url="https://example.com/repository",
        user_id=owner.id,
        project_type_id=project_type.id,
    )
    session.add(project)
    session.commit()

    with pytest.raises(ProjectTypeNotFoundError):
        update_project(
            session,
            project.id,
            ProjectUpdate(name="Changed name", project_type_id=uuid4()),
            user_id=owner.id,
        )

    assert project.name == "Original name"
