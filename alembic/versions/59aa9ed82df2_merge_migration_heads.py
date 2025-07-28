"""merge migration heads

Revision ID: 59aa9ed82df2
Revises: e0cac95b8bfc, f1d8a951e28d
Create Date: 2025-07-28 13:30:23.413443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59aa9ed82df2'
down_revision: Union[str, None] = ('e0cac95b8bfc', 'f1d8a951e28d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
