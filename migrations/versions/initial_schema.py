"""Initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2025-01-02 07:49:35.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""
    # Create email table
    op.create_table(
        'email',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('subject', sa.String(500)),
        sa.Column('body', sa.Text()),
        sa.Column('from_address', sa.String(255)),
        sa.Column('to_address', sa.String(255)),
        sa.Column('received_at', sa.DateTime()),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id', name='pk_email')
    )

    # Create analysis table
    op.create_table(
        'analysis',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('email_id', sa.String(100), nullable=False),
        sa.Column('summary', sa.String(1000)),
        sa.Column('sentiment', sa.String(20), default='neutral'),
        sa.Column('key_points', sa.JSON(), default='[]'),
        sa.Column('action_items', sa.JSON(), default='[]'),
        sa.Column('analyzed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id', name='pk_analysis'),
        sa.ForeignKeyConstraint(['email_id'], ['email.id'], name='fk_analysis_email_id')
    )

    # Create indexes
    op.create_index('ix_email_subject', 'email', ['subject'])
    op.create_index('ix_analysis_email_id', 'analysis', ['email_id'])


def downgrade() -> None:
    """Remove schema."""
    # Drop indexes
    op.drop_index('ix_analysis_email_id')
    op.drop_index('ix_email_subject')

    # Drop tables
    op.drop_table('analysis')
    op.drop_table('email')
