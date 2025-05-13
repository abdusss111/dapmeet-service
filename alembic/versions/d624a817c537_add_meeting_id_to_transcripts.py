"""Add meeting_id to transcripts

Revision ID: d624a817c537
Revises: c9e54922555e
Create Date: 2025-05-12 11:10:58.043735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd624a817c537'
down_revision: Union[str, None] = 'c9e54922555e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
