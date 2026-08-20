from sqlmodel import Session

from app.models.label import Label
from app.models.profile import Profile
from app.models.project import Project
from app.models.project_type import ProjectType
from app.models.user import User
from app.services.project_queries import count_projects, list_projects


def test_project_search__expect_sql_wildcards_treated_as_literal_text(
    session: Session,
) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    project_type = ProjectType(name="Bot")
    session.add_all([owner, project_type])
    session.flush()
    session.add_all(
        [
            _project(
                name="100% Matrix",
                owner=owner,
                project_type=project_type,
            ),
            _project(
                name="1000 Matrix",
                owner=owner,
                project_type=project_type,
            ),
            _project(
                name="under_score",
                owner=owner,
                project_type=project_type,
            ),
            _project(
                name="underXscore",
                owner=owner,
                project_type=project_type,
            ),
        ]
    )
    session.commit()

    percent_matches = list_projects(session, query="100%")
    underscore_matches = list_projects(session, query="under_score")

    assert [project.name for project in percent_matches] == ["100% Matrix"]
    assert [project.name for project in underscore_matches] == ["under_score"]


def test_count_projects__expect_same_filters_as_project_list(session: Session) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    bot_type = ProjectType(name="Bot")
    sdk_type = ProjectType(name="SDK")
    utility_label = Label(name="Utility")
    session.add_all([owner, bot_type, sdk_type, utility_label])
    session.flush()
    session.add_all(
        [
            _project(
                name="Utility Bot",
                owner=owner,
                project_type=bot_type,
                labels=[utility_label],
            ),
            _project(
                name="Example SDK",
                owner=owner,
                project_type=sdk_type,
            ),
        ]
    )
    session.commit()

    assert count_projects(session) == 2
    assert count_projects(session, project_type="Bot") == 1
    assert count_projects(session, label="Utility") == 1
    assert count_projects(session, query="SDK") == 1


def test_list_projects__expect_response_relationships_eagerly_loaded(
    session: Session,
) -> None:
    owner = User(oidc_issuer="issuer", oidc_subject="owner")
    owner.profile = Profile(display_name="Maintainer")
    project_type = ProjectType(name="Bot")
    label = Label(name="Utility")
    session.add_all([owner, project_type, label])
    session.flush()
    session.add(
        _project(
            name="Example Bot",
            owner=owner,
            project_type=project_type,
            labels=[label],
        )
    )
    session.commit()

    project = list_projects(session)[0]
    session.expunge_all()

    assert project.project_type.name == "Bot"
    assert [item.name for item in project.labels] == ["Utility"]
    assert project.owner.profile is not None
    assert project.owner.profile.display_name == "Maintainer"


def _project(
    *,
    name: str,
    owner: User,
    project_type: ProjectType,
    labels: list[Label] | None = None,
) -> Project:
    return Project(
        name=name,
        short_description=name,
        description=f"Description for {name}",
        repository_url="https://example.com/project",
        user_id=owner.id,
        project_type_id=project_type.id,
        labels=labels or [],
    )
