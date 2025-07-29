"""Add transcript_segments table

Revision ID: 8a88098e60cd
Revises: 31c0a7fe20eb
Create Date: 2025-06-21 10:21:18.117907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a88098e60cd'
down_revision: Union[str, None] = '31c0a7fe20eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
