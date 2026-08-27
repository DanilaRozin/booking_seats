"""merge_cafe_and_media_migration_chains

Revision ID: 8ae1e05a39d1
Revises: 49183e54f3bd
Create Date: 2026-08-26 17:00:13.124936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ae1e05a39d1'
down_revision: Union[str, Sequence[str], None] = '49183e54f3bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
