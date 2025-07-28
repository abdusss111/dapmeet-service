"""Add meeting_id to Transcript

Revision ID: 3dc269adbebc
Revises: 859f7e523989
Create Date: 2025-05-08 18:20:30.139598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dc269adbebc'
down_revision: Union[str, None] = '859f7e523989'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
