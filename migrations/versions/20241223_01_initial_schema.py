"""Initial schema

Revision ID: 20241223_01
Revises: 
Create Date: 2024-12-20 07:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241223_01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create emails table
    op.create_table(
        'emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sender', sa.String(200), nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=True),
        sa.Column('labels', sa.String(500), nullable=True),
        sa.Column('thread_id', sa.String(100), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create email_analysis table
    op.create_table(
        'email_analysis',
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('analysis_date', sa.DateTime(), nullable=True),
        sa.Column('analyzed_date', sa.DateTime(), nullable=False),
        sa.Column('prompt_version', sa.String(50), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('category', sa.JSON(), nullable=False),
        sa.Column('priority_score', sa.Integer(), nullable=False),
        sa.Column('priority_reason', sa.String(), nullable=False),
        sa.Column('action_needed', sa.Boolean(), nullable=False),
        sa.Column('action_type', sa.JSON(), nullable=False),
        sa.Column('action_deadline', sa.String(), nullable=True),
        sa.Column('key_points', sa.JSON(), nullable=False),
        sa.Column('people_mentioned', sa.JSON(), nullable=False),
        sa.Column('links_found', sa.JSON(), nullable=False),
        sa.Column('links_display', sa.JSON(), nullable=False),
        sa.Column('project', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('ref_docs', sa.String(), nullable=True),
        sa.Column('sentiment', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('raw_analysis', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id']),
        sa.PrimaryKeyConstraint('email_id')
    )


def downgrade() -> None:
    op.drop_table('email_analysis')
    op.drop_table('emails')
