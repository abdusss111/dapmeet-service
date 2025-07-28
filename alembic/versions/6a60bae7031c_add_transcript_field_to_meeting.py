"""Add transcript field to Meeting

Revision ID: 6a60bae7031c
Revises: d624a817c537
Create Date: 2025-05-12 11:12:19.215132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a60bae7031c'
down_revision: Union[str, None] = 'd624a817c537'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
