from uuid import uuid4, UUID

from app.models.project import Project


def test_project_model_creation__expect_uuid_identifiers_assigned() -> None:
    user_id = uuid4()
    project_type_id = uuid4()
    project = Project(
        name="Test",
        description="Test project",
        short_description="Test project",
        repository_url="",
        website_url="",
        matrix_server_url="",
        user_id=user_id,
        project_type_id=project_type_id,
        supports_e2ee=False,
    )

    assert isinstance(project.id, UUID)
    assert project.user_id == user_id
    assert project.project_type_id == project_type_id
