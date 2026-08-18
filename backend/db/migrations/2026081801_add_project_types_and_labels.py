"""Split project categories into one project type and optional labels."""

from pelican import change_table, create_table, drop_table, get_runner, migration
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


def _create_named_lookup(table_name: str) -> None:
    with create_table(table_name) as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.string("name", length=100, nullable=False)
        table.timestamps()
        table.index(["name"], unique=True)


def _create_project_labels() -> None:
    with create_table("project_labels", primary_key=False) as table:
        table.column(
            "project_id",
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        )
        table.column(
            "label_id",
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        )
        table.add_foreign_key(
            ["project_id"],
            "projects",
            ["id"],
            name="project_labels_project_id_fkey",
            on_delete="CASCADE",
        )
        table.add_foreign_key(
            ["label_id"],
            "labels",
            ["id"],
            name="project_labels_label_id_fkey",
            on_delete="CASCADE",
        )
        table.index(["project_id", "label_id"], unique=True)
        table.index(["label_id"])


@migration.up
def upgrade() -> None:
    _create_named_lookup("project_types")
    _create_named_lookup("labels")
    _create_project_labels()

    with change_table("projects") as table:
        table.column("project_type_id", PostgreSQLUUID(as_uuid=True), nullable=True)

    with change_table("projects") as table:
        table.add_foreign_key(
            ["project_type_id"],
            "project_types",
            ["id"],
            name="projects_project_type_id_fkey",
        )
        table.index(["project_type_id"])

    with get_runner().engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO labels (id, name, created_at, updated_at)
            SELECT id, name, created_at, updated_at
            FROM categories
        """))
        connection.execute(text("""
            INSERT INTO project_labels (project_id, label_id)
            SELECT project_id, category_id
            FROM project_categories
        """))
        connection.execute(text("""
            INSERT INTO project_types (name, created_at, updated_at)
            VALUES
                ('Bot', NOW(), NOW()),
                ('SDK', NOW(), NOW()),
                ('Framework', NOW(), NOW()),
                ('Bridges', NOW(), NOW()),
                ('Clients', NOW(), NOW()),
                ('Server', NOW(), NOW()),
                ('Integrations', NOW(), NOW())
        """))
        connection.execute(text("""
            UPDATE projects
            SET project_type_id = (
                SELECT id FROM project_types WHERE name = 'Bot'
            )
        """))

    with change_table("projects") as table:
        table.alter("project_type_id", nullable=False)

    drop_table("project_categories")
    drop_table("categories")


@migration.down
def downgrade() -> None:
    _create_named_lookup("categories")

    with create_table("project_categories", primary_key=False) as table:
        table.column(
            "project_id",
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        )
        table.column(
            "category_id",
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
            primary_key=True,
        )
        table.add_foreign_key(
            ["project_id"],
            "projects",
            ["id"],
            name="project_categories_project_id_fkey",
            on_delete="CASCADE",
        )
        table.add_foreign_key(
            ["category_id"],
            "categories",
            ["id"],
            name="project_categories_category_id_fkey",
            on_delete="CASCADE",
        )
        table.index(["project_id", "category_id"], unique=True)
        table.index(["category_id"])

    with get_runner().engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO categories (id, name, created_at, updated_at)
            SELECT id, name, created_at, updated_at
            FROM labels
        """))
        connection.execute(text("""
            INSERT INTO project_categories (project_id, category_id)
            SELECT project_id, label_id
            FROM project_labels
        """))

    with change_table("projects") as table:
        table.remove_index(["project_type_id"])
        table.remove_foreign_key(name="projects_project_type_id_fkey")

    with change_table("projects") as table:
        table.drop("project_type_id")

    drop_table("project_labels")
    drop_table("labels")
    drop_table("project_types")
