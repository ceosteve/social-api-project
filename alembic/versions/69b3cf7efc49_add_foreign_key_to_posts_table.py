"""add foreign key to posts table

Revision ID: 69b3cf7efc49
Revises: c21e3e4a5436
Create Date: 2025-08-28 15:19:36.294930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69b3cf7efc49'
down_revision: Union[str, Sequence[str], None] = 'c21e3e4a5436'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('owner_id',sa.Integer(), nullable=False))
    op.create_foreign_key('posts_user_fk',source_table="posts", referent_table="users",
                          local_cols=['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    op.drop_constraint('posts_user_fk',table_name='posts')
    op.drop_column('posts','owner_id')
    pass
