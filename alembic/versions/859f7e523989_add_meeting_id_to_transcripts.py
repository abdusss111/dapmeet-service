"""Add meeting_id to transcripts

Revision ID: 859f7e523989
Revises: 2d03c9617378
Create Date: 2025-05-08 18:19:22.488243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '859f7e523989'
down_revision: Union[str, None] = '2d03c9617378'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
