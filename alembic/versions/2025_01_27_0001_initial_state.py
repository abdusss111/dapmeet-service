"""initial state

Revision ID: 2025_01_27_0001
Revises: 
Create Date: 2025-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_01_27_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration represents the current state of the database
    # No changes needed - this is just to establish a clean base
    pass


def downgrade() -> None:
    # No downgrade needed
    pass
