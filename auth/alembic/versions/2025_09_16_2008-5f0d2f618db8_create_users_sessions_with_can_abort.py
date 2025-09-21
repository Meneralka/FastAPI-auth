"""Create Users, Sessions with can_abort

Revision ID: 5f0d2f618db8
Revises:
Create Date: 2025-09-16 20:08:17.151804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5f0d2f618db8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sessions",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "EXPIRED", "DISABLED", name="session_status"),
            nullable=False,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("sub", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("can_abort", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
    )
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=22), nullable=False),
        sa.Column("hashed_password", postgresql.BYTEA(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    op.drop_table("sessions")
    op.execute("DROP TYPE IF EXISTS session_status;")
