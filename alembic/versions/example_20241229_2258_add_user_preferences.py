"""add user preferences table

Revision ID: example_20241229_2258
Revises: 
Create Date: 2024-12-29 22:58:51.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'example_20241229_2258'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user preferences table."""
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('preference_key', sa.String(length=50), nullable=False),
        sa.Column('preference_value', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'preference_key', name='uq_user_preference')
    )
    op.create_index(
        'ix_user_preferences_user_id',
        'user_preferences',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove user preferences table."""
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    op.drop_table('user_preferences')
