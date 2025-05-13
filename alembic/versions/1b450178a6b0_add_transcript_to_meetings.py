"""Add transcript to meetings

Revision ID: 1b450178a6b0
Revises: 6a60bae7031c
Create Date: 2025-05-12 11:14:27.855123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b450178a6b0'
down_revision: Union[str, None] = '6a60bae7031c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
