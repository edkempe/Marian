"""Initial schema with updated field sizes and types

This migration creates the initial schema with:
1. Email table with:
   - labels field as VARCHAR(150) for longer label IDs
   - has_attachments column
   - full_api_response for complete Gmail API data
2. Gmail Labels table with:
   - label_id as VARCHAR(30)
   - History tracking columns
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '20241223_01'
down_revision = None  # Initial migration
branch_labels = None
depends_on = None

def upgrade():
    # Create emails table
    op.create_table('emails',
        sa.Column('id', sa.Text, primary_key=True),
        sa.Column('thread_id', sa.Text),
        sa.Column('subject', sa.Text),
        sa.Column('sender', sa.Text),
        sa.Column('date', sa.Text),
        sa.Column('body', sa.Text),
        sa.Column('labels', sa.String(150)),
        sa.Column('has_attachments', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('full_api_response', sa.Text)
    )

    # Create gmail_labels table
    op.create_table('gmail_labels',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('label_id', sa.String(30), nullable=False, unique=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('type', sa.Text),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='1'),
        sa.Column('first_seen_at', sa.DateTime, nullable=False, 
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_seen_at', sa.DateTime, nullable=False,
                 server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )

def downgrade():
    op.drop_table('gmail_labels')
    op.drop_table('emails')
