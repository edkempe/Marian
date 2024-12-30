"""add user settings table

Revision ID: example_20241229_2302
Revises: example_20241229_2258
Create Date: 2024-12-29 23:02:21.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'example_20241229_2302'
down_revision: Union[str, None] = 'example_20241229_2258'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user settings table."""
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='light'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_settings')
    )
    op.create_index(
        'ix_user_settings_user_id',
        'user_settings',
        ['user_id'],
        unique=True
    )


def downgrade() -> None:
    """Remove user settings table."""
    op.drop_index('ix_user_settings_user_id', 'user_settings')
    op.drop_table('user_settings')
