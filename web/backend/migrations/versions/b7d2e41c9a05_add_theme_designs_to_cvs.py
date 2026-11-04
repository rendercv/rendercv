"""add theme_designs to cvs

Why:
    Switching theme rewrites the whole design document from the new theme's
    defaults, so switching back used to throw away every value the user had
    tuned (spacing chosen to keep a CV on one page, say). `theme_designs`
    keeps, per CV, the design each theme had when the user last left it, so
    the editor can put it back. It lives on the `cvs` row rather than in
    `preferences` so it is deleted and duplicated with the CV, and is not
    held to the 4096-character preference cap.

    `NOT NULL` with a server default of `{}` so existing rows get an empty
    map in the same statement, with no data backfill step.

Revision ID: b7d2e41c9a05
Revises: 320e31bb905f
Create Date: 2026-11-04 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7d2e41c9a05"
down_revision: str | Sequence[str] | None = "320e31bb905f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add `cvs.theme_designs`, empty for every existing CV."""
    with op.batch_alter_table("cvs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("theme_designs", sa.Text(), nullable=False, server_default="{}")
        )


def downgrade() -> None:
    """Drop `cvs.theme_designs`; CVs keep their current design."""
    with op.batch_alter_table("cvs", schema=None) as batch_op:
        batch_op.drop_column("theme_designs")
