"""add oauth identity columns to users

Why:
    Phase 6 of the web editor plan (docs/plans/completed/cv-editor-web-app.md):
    Google sign-in. The baseline `users` row is an anonymous device session
    keyed by `session_token`; these four nullable columns let that same row
    also carry an account identity, which is what allows an anonymous
    session to be claimed by an account without moving its CVs to a
    different table (`rendercv_web.db.repository.claim_anonymous_user`).

    All four are nullable because every existing row is anonymous and has
    none of them. The unique constraint on
    `(auth_provider, auth_provider_id)` is what makes signing in on a
    second device find the existing account instead of creating a
    duplicate; SQLite treats NULLs as distinct, so it does not constrain
    anonymous rows.

Revision ID: 320e31bb905f
Revises: 8a6ebf56c34d
Create Date: 2026-08-28 19:55:59.816809

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "320e31bb905f"
down_revision: str | Sequence[str] | None = "8a6ebf56c34d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the nullable account-identity columns and their unique constraint."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("auth_provider", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(
            sa.Column("auth_provider_id", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(sa.Column("email", sa.String(length=320), nullable=True))
        batch_op.add_column(
            sa.Column("display_name", sa.String(length=255), nullable=True)
        )
        batch_op.create_unique_constraint(
            "uq_users_auth_provider_identity", ["auth_provider", "auth_provider_id"]
        )


def downgrade() -> None:
    """Drop the account-identity columns, returning `users` to anonymous-only."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_users_auth_provider_identity", type_="unique")
        batch_op.drop_column("display_name")
        batch_op.drop_column("email")
        batch_op.drop_column("auth_provider_id")
        batch_op.drop_column("auth_provider")
