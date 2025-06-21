"""Add transcript_segments table

Revision ID: 4ef5400b039a
Revises: 6e140d245736
Create Date: 2025-06-21 10:17:59.246885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ef5400b039a'
down_revision: Union[str, None] = '6e140d245736'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
