"""Add private Matrix refresh tokens and original avatar media URIs."""

from pelican import change_table, create_table, drop_table, migration
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


@migration.up
def upgrade() -> None:
    with create_table("matrix_oauth_credentials") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.column("user_id", PostgreSQLUUID(as_uuid=True), nullable=False)
        table.string("refresh_token_encrypted", length=4096, nullable=False)
        table.timestamps()
        table.index(["user_id"], unique=True)
        table.add_foreign_key(
            ["user_id"],
            "users",
            ["id"],
            name="matrix_oauth_credentials_user_id_fkey",
            on_delete="CASCADE",
        )

    with change_table("profiles") as table:
        table.string("matrix_avatar_mxc", length=500, nullable=True)


@migration.down
def downgrade() -> None:
    with change_table("profiles") as table:
        table.drop("matrix_avatar_mxc")

    drop_table("matrix_oauth_credentials")
