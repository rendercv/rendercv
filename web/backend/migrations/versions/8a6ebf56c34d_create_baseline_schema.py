"""create baseline schema

Why:
    Phase 4a of the web editor plan (docs/plans/completed/cv-editor-web-app.md):
    the four baseline tables backing anonymous-session accounts, multi-CV
    storage, autosave version history, and UI preferences. See
    `rendercv_web.db.models` for the column-by-column rationale and
    `rendercv_web.db.repository` for the access patterns each index serves.

Revision ID: 8a6ebf56c34d
Revises:
Create Date: 2026-08-26 18:57:34.397483

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8a6ebf56c34d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create `users`, `cvs`, `preferences`, and `cv_versions`."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_token", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_users_session_token"), ["session_token"], unique=True
        )

    op.create_table(
        "cvs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cv_yaml", sa.Text(), nullable=False),
        sa.Column("design_yaml", sa.Text(), nullable=False),
        sa.Column("locale_yaml", sa.Text(), nullable=False),
        sa.Column("settings_yaml", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("cvs", schema=None) as batch_op:
        batch_op.create_index(
            "ix_cvs_user_id_updated_at", ["user_id", "updated_at"], unique=False
        )

    op.create_table(
        "preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "key"),
    )

    op.create_table(
        "cv_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cv_id", sa.Integer(), nullable=False),
        sa.Column("cv_yaml", sa.Text(), nullable=False),
        sa.Column("design_yaml", sa.Text(), nullable=False),
        sa.Column("locale_yaml", sa.Text(), nullable=False),
        sa.Column("settings_yaml", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["cv_id"], ["cvs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("cv_versions", schema=None) as batch_op:
        batch_op.create_index(
            "ix_cv_versions_cv_id_created_at", ["cv_id", "created_at"], unique=False
        )


def downgrade() -> None:
    """Drop the four baseline tables, children before parents."""
    with op.batch_alter_table("cv_versions", schema=None) as batch_op:
        batch_op.drop_index("ix_cv_versions_cv_id_created_at")
    op.drop_table("cv_versions")

    op.drop_table("preferences")

    with op.batch_alter_table("cvs", schema=None) as batch_op:
        batch_op.drop_index("ix_cvs_user_id_updated_at")
    op.drop_table("cvs")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_session_token"))
    op.drop_table("users")
