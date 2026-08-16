"""Add user profiles and move Matrix identity out of users."""

from pelican import (
    change_table,
    create_table,
    drop_table,
    get_runner,
    migration,
)
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


@migration.up
def upgrade() -> None:
    with create_table("profiles") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )

        table.column(
            "user_id",
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
        )

        table.string(
            "matrix_id",
            length=255,
            nullable=True,
        )

        table.boolean(
            "matrix_id_verified",
            nullable=False,
            default=False,
        )

        table.string(
            "display_name",
            length=100,
            nullable=True,
        )

        table.string(
            "bio",
            length=1024,
            nullable=True,
        )

        table.string(
            "avatar_url",
            length=500,
            nullable=True,
        )

        table.string(
            "github_url",
            length=150,
            nullable=True,
        )

        table.string(
            "website_url",
            length=150,
            nullable=True,
        )

        table.timestamps()

        # One profile per user.
        table.index(
            ["user_id"],
            unique=True,
        )

        # A Matrix ID can only belong to one profile.
        table.index(
            ["matrix_id"],
            unique=True,
        )

        # Add this as a Pelican operation instead of an inline
        # SQLAlchemy ForeignKey.
        table.add_foreign_key(
            ["user_id"],
            "users",
            ["id"],
            name="profiles_user_id_fkey",
            on_delete="CASCADE",
        )

    # Move existing Matrix IDs into profiles.
    with get_runner().engine.begin() as connection:
        connection.execute(text("""
                INSERT INTO profiles (
                    user_id,
                    matrix_id,
                    matrix_id_verified,
                    created_at,
                    updated_at
                )
                SELECT
                    id,
                    matrix_id,
                    FALSE,
                    created_at,
                    updated_at
                FROM users
                WHERE matrix_id IS NOT NULL
            """))

    # Matrix identity now belongs to Profile.
    with change_table("users") as table:
        table.remove_index(["matrix_id"])

    with change_table("users") as table:
        table.drop("matrix_id")


@migration.down
def downgrade() -> None:
    # Restore users.matrix_id.
    with change_table("users") as table:
        table.string(
            "matrix_id",
            length=255,
            nullable=True,
        )

    # Copy the profile Matrix IDs back.
    with get_runner().engine.begin() as connection:
        connection.execute(text("""
                UPDATE users
                SET matrix_id = profiles.matrix_id
                FROM profiles
                WHERE profiles.user_id = users.id
            """))

    with change_table("users") as table:
        table.index(
            ["matrix_id"],
            unique=True,
        )

    drop_table("profiles")
