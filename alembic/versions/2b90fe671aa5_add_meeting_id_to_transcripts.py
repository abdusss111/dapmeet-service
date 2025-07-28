"""Add meeting_id to transcripts

Revision ID: 2b90fe671aa5
Revises: 3dc269adbebc
Create Date: 2025-05-08 18:35:39.759272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b90fe671aa5'
down_revision: Union[str, None] = '3dc269adbebc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
