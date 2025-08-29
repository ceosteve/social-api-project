"""add content column to posts table

Revision ID: 32d4fc86c917
Revises: 271745055dd9
Create Date: 2025-08-28 14:57:21.089972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32d4fc86c917'
down_revision: Union[str, Sequence[str], None] = '271745055dd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('content', sa.String(), nullable=False))

    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
