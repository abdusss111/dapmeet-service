"""Add transcript_segments table

Revision ID: 16becf9e6fc6
Revises: 8a88098e60cd
Create Date: 2025-06-21 10:34:01.177291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16becf9e6fc6'
down_revision: Union[str, None] = '8a88098e60cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
