"""Add chat_history to Meeting

Revision ID: 6e140d245736
Revises: 577623eaa0c4
Create Date: 2025-05-14 06:36:04.442555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e140d245736'
down_revision: Union[str, None] = '577623eaa0c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
