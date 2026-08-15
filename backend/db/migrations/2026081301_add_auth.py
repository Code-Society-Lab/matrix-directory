"""Add Matrix OIDC identities and local application sessions."""

from pelican import change_table, create_table, drop_table, get_runner, migration
from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


@migration.up
def upgrade() -> None:
    with change_table("users") as table:
        table.alter("matrix_id", nullable=True)
        table.string("oidc_issuer", length=255, nullable=True)
        table.string("oidc_subject", length=255, nullable=True)

    with change_table("users") as table:
        table.index(["oidc_issuer", "oidc_subject"], unique=True)

    with create_table("auth_sessions") as table:
        table.column(
            "id",
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
        table.string("token_hash", length=64, nullable=False)
        table.column(
            "user_id",
            PostgreSQLUUID(as_uuid=True),
            ForeignKey("users.id"),
            nullable=False,
        )
        table.column("expires_at", DateTime(), nullable=False)
        table.column("created_at", DateTime(), nullable=False)
        table.index(["token_hash"], unique=True)
        table.index(["user_id"])


@migration.down
def downgrade() -> None:
    with get_runner().engine.connect() as connection:
        has_auth_data = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE matrix_id IS NULL
                       OR oidc_issuer IS NOT NULL
                       OR oidc_subject IS NOT NULL
                    UNION ALL
                    SELECT 1 FROM auth_sessions
                )
                """)).scalar()

    if has_auth_data:
        raise RuntimeError(
            "Cannot downgrade auth migration after OIDC identities or sessions exist"
        )

    drop_table("auth_sessions")
    with change_table("users") as table:
        table.remove_index(["oidc_issuer", "oidc_subject"])

    with change_table("users") as table:
        table.drop("oidc_subject")
        table.drop("oidc_issuer")
        table.alter("matrix_id", nullable=False)
