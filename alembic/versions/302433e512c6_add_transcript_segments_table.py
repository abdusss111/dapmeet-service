"""Add transcript_segments table

Revision ID: 302433e512c6
Revises: 16becf9e6fc6
Create Date: 2025-06-21 11:42:43.068752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '302433e512c6'
down_revision: Union[str, None] = '16becf9e6fc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
