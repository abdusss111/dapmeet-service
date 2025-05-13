"""Add transcript to meetings

Revision ID: 110ec746245c
Revises: 1b450178a6b0
Create Date: 2025-05-12 11:22:09.073011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '110ec746245c'
down_revision: Union[str, None] = '1b450178a6b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
