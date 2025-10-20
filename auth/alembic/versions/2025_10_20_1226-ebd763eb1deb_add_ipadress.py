"""Add ipAdress

Revision ID: ebd763eb1deb
Revises: 5f0d2f618db8
Create Date: 2025-10-20 12:26:35.241706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ebd763eb1deb"
down_revision: Union[str, Sequence[str], None] = "5f0d2f618db8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("sessions", sa.Column("ip", sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sessions", "ip")
