"""Remove Transcript model and move transcript to Meeting

Revision ID: c9e54922555e
Revises: 9818309dc96a
Create Date: 2025-05-12 11:08:57.694965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e54922555e'
down_revision: Union[str, None] = '9818309dc96a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
