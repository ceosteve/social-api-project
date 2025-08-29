"""add last two columns to the posts table

Revision ID: 9df776fbe974
Revises: 69b3cf7efc49
Create Date: 2025-08-28 15:52:00.869717

"""
from pydoc import text
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9df776fbe974'
down_revision: Union[str, Sequence[str], None] = '69b3cf7efc49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('published',
                                    sa.Boolean(),nullable=False, server_default='TRUE'))
    op.add_column('posts',sa.Column('created_at',sa.TIMESTAMP(timezone=True),
                                    nullable=False,server_default=sa.text('now()')))
    pass


def downgrade() -> None:
    op.drop_column('posts','published')
    op.drop_column('posts','created_at')
    pass
