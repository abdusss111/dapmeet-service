"""create_all_tables

Revision ID: 73cfc96116d0
Revises: 8118726296e9
Create Date: 2025-06-21 12:19:36.936477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73cfc96116d0'
down_revision: Union[str, None] = '8118726296e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
