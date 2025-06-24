"""create_transcript_segments_table

Revision ID: 8118726296e9
Revises: 302433e512c6
Create Date: 2025-06-21 12:15:27.009142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8118726296e9'
down_revision: Union[str, None] = '302433e512c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
