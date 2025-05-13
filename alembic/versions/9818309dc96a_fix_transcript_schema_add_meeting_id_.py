"""Fix transcript schema: add meeting_id, remove title and speaker_json

Revision ID: 9818309dc96a
Revises: 2b90fe671aa5
Create Date: 2025-05-08 18:37:31.379857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9818309dc96a'
down_revision: Union[str, None] = '2b90fe671aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
