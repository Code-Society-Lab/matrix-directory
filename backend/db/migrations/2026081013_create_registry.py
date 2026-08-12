"""202608121415 - Create project registry

┌───────────────┐
|    users      |
|---------------|
│ id            │
│ matrix_id     │
│ created_at    │
│ updated_at    │
└───────┬───────┘
        │ 1
        │
        │ *
┌───────▼────────────┐
│    projects        │
|--------------------|
│ id                 │
│ name               │
│ description        │
│ short_description  │
│ repository_url     │
│ website_url        │
│ matrix_server_url  │
│ user_id            │
│ supports_e2ee      │
└────────┬───────────┘
         │
         │ *
         ▼
┌────────────────────┐
│ project_categories │
|--------------------|
│ project_id         │
│ category_id        │
└─────────┬──────────┘
          │ *
          │
          │ 1
     ┌────▼─────┐
     │categories│
     |----------|
     │ id       │
     │ name     │
     └──────────┘
"""

from pelican import create_table, drop_table, migration
from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


@migration.up
def upgrade() -> None:
    # Users who own/submit projects.
    with create_table("users") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.string(
            "matrix_id",
            length=255,
            nullable=False,
        )

        table.timestamps()

        table.index(["matrix_id"], unique=True)

    # Categories available to projects.
    with create_table("categories") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.string(
            "name",
            length=100,
            nullable=False,
        )

        table.timestamps()

        table.index(["name"], unique=True)

    # Matrix projects listed in the registry.
    with create_table("projects") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.string(
            "name",
            length=100,
            nullable=False,
        )

        table.text(
            "description",
            nullable=False,
        )

        table.string(
            "short_description",
            length=240,
            nullable=False,
        )

        table.string(
            "repository_url",
            nullable=True,
        )

        table.string(
            "website_url",
            nullable=True,
        )

        table.string(
            "matrix_server_url",
            nullable=True,
        )

        # user_id -> users.id
        table.column(
            "user_id",
            PostgreSQLUUID(as_uuid=True),
            ForeignKey("users.id"),
            nullable=False,
        )

        table.boolean(
            "supports_e2ee",
            nullable=False,
            default=False,
        )

        table.timestamps()

        table.index(["name"])
        table.index(["user_id"])

    # Many-to-many relationship:
    #
    # Project * <-> * Category
    #
    with create_table("project_categories", primary_key=False) as table:
        # project_id -> projects.id
        table.column(
            "project_id",
            PostgreSQLUUID(as_uuid=True),
            ForeignKey("projects.id"),
            primary_key=True,
            nullable=False,
        )

        # category_id -> categories.id
        table.column(
            "category_id",
            PostgreSQLUUID(as_uuid=True),
            ForeignKey("categories.id"),
            primary_key=True,
            nullable=False,
        )

        # Prevent:
        #
        # project_id | category_id
        # -----------+------------
        # 1          | 3
        # 1          | 3   <- duplicate
        #
        table.index(
            ["project_id", "category_id"],
            unique=True,
        )

        table.index(["category_id"])


@migration.down
def downgrade() -> None:
    drop_table("project_categories")
    drop_table("projects")
    drop_table("categories")
    drop_table("users")
