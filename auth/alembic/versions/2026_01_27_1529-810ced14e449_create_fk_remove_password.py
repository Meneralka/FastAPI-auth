"""create FK, remove password

Revision ID: 810ced14e449
Revises: ebd763eb1deb
Create Date: 2026-01-27 15:29:45.683041

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "810ced14e449"
down_revision: Union[str, Sequence[str], None] = "ebd763eb1deb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        op.f("fk_sessions_sub_users"),
        "sessions",
        "users",
        ["sub"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("users", "hashed_password")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            postgresql.BYTEA(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_constraint(op.f("fk_sessions_sub_users"), "sessions", type_="foreignkey")
