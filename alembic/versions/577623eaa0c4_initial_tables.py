"""Initial tables

Revision ID: 577623eaa0c4
Revises: 110ec746245c
Create Date: 2025-05-13 13:03:30.574308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '577623eaa0c4'
down_revision: Union[str, None] = '110ec746245c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
