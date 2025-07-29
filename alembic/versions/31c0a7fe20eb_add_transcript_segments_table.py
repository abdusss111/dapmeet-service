"""Add transcript_segments table

Revision ID: 31c0a7fe20eb
Revises: 4ef5400b039a
Create Date: 2025-06-21 10:18:23.951700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31c0a7fe20eb'
down_revision: Union[str, None] = '4ef5400b039a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
