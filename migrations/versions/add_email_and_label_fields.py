"""Add additional fields to Email and GmailLabel models.

Revision ID: add_email_and_label_fields
Revises: initial_schema
Create Date: 2024-12-28 08:48:49.000000

This migration adds:
1. Email fields:
   - to_address: Recipient email address
   - full_api_response: Complete Gmail API response

2. GmailLabel fields:
   - is_active: Whether the label is currently active
   - first_seen_at: When the label was first seen
   - last_seen_at: When the label was last seen
   - deleted_at: When the label was deleted (if applicable)
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = 'add_email_and_label_fields'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None

def upgrade():
    """Add new fields to Email and GmailLabel tables."""
    # Add fields to emails table
    with op.batch_alter_table('emails') as batch_op:
        batch_op.add_column(sa.Column('to_address', sa.String(200)))
        batch_op.add_column(sa.Column('full_api_response', sa.Text(), 
                                    server_default='{}'))

    # Add fields to gmail_labels table
    with op.batch_alter_table('gmail_labels') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), 
                                    nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('first_seen_at', sa.DateTime(), 
                                    nullable=False, 
                                    server_default=sa.func.current_timestamp()))
        batch_op.add_column(sa.Column('last_seen_at', sa.DateTime(), 
                                    nullable=False, 
                                    server_default=sa.func.current_timestamp()))
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime()))

def downgrade():
    """Remove added fields from Email and GmailLabel tables."""
    # Remove fields from emails table
    with op.batch_alter_table('emails') as batch_op:
        batch_op.drop_column('to_address')
        batch_op.drop_column('full_api_response')

    # Remove fields from gmail_labels table
    with op.batch_alter_table('gmail_labels') as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('first_seen_at')
        batch_op.drop_column('last_seen_at')
        batch_op.drop_column('deleted_at')
