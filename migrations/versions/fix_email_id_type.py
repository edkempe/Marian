"""Fix Email ID type to match Gmail API.

Revision ID: fix_email_id_type
Revises: add_email_and_label_fields
Create Date: 2024-12-28 09:06:00.000000

This migration changes the Email.id column from INTEGER to VARCHAR(100) to match
the Gmail API's message ID format. The Gmail API uses string IDs for both messages
and threads, so our database schema should reflect this.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'fix_email_id_type'
down_revision = 'add_email_and_label_fields'
branch_labels = None
depends_on = None

def upgrade():
    """Change Email.id from INTEGER to VARCHAR(100)."""
    # SQLite doesn't support ALTER COLUMN, so we need to:
    # 1. Create a new table with the correct schema
    # 2. Copy data from old table
    # 3. Drop old table
    # 4. Rename new table to old name
    
    # Create new table
    op.create_table(
        'emails_new',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sender', sa.String(200), nullable=True),
        sa.Column('to_address', sa.String(200), nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=True),
        sa.Column('labels', sa.String(500), nullable=True),
        sa.Column('threadId', sa.String(100), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.Column('cc_address', sa.Text(), server_default="''''''"),
        sa.Column('bcc_address', sa.Text(), server_default="''''''"),
        sa.Column('full_api_response', sa.Text(), server_default='{}'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data
    op.execute('''
        INSERT INTO emails_new 
        SELECT CAST(id AS VARCHAR), subject, body, sender, to_address, 
               received_date, labels, threadId, has_attachments, 
               cc_address, bcc_address, full_api_response
        FROM emails
    ''')
    
    # Update foreign key in email_analysis
    op.drop_constraint('email_analysis_email_id_fkey', 'email_analysis', type_='foreignkey')
    op.execute('''
        UPDATE email_analysis 
        SET email_id = CAST(email_id AS VARCHAR)
    ''')
    
    # Drop old table and rename new
    op.drop_table('emails')
    op.rename_table('emails_new', 'emails')
    
    # Re-add foreign key with new type
    with op.batch_alter_table('email_analysis') as batch_op:
        batch_op.alter_column('email_id',
                            existing_type=sa.Integer(),
                            type_=sa.String(100),
                            existing_nullable=False)
        batch_op.create_foreign_key(
            'email_analysis_email_id_fkey',
            'emails',
            ['email_id'],
            ['id']
        )

def downgrade():
    """Change Email.id back to INTEGER."""
    # Create new table
    op.create_table(
        'emails_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sender', sa.String(200), nullable=True),
        sa.Column('to_address', sa.String(200), nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=True),
        sa.Column('labels', sa.String(500), nullable=True),
        sa.Column('threadId', sa.String(100), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.Column('cc_address', sa.Text(), server_default="''''''"),
        sa.Column('bcc_address', sa.Text(), server_default="''''''"),
        sa.Column('full_api_response', sa.Text(), server_default='{}'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data
    op.execute('''
        INSERT INTO emails_new 
        SELECT CAST(id AS INTEGER), subject, body, sender, to_address, 
               received_date, labels, threadId, has_attachments, 
               cc_address, bcc_address, full_api_response
        FROM emails
    ''')
    
    # Update foreign key in email_analysis
    op.drop_constraint('email_analysis_email_id_fkey', 'email_analysis', type_='foreignkey')
    op.execute('''
        UPDATE email_analysis 
        SET email_id = CAST(email_id AS INTEGER)
    ''')
    
    # Drop old table and rename new
    op.drop_table('emails')
    op.rename_table('emails_new', 'emails')
    
    # Re-add foreign key with new type
    with op.batch_alter_table('email_analysis') as batch_op:
        batch_op.alter_column('email_id',
                            existing_type=sa.String(100),
                            type_=sa.Integer(),
                            existing_nullable=False)
        batch_op.create_foreign_key(
            'email_analysis_email_id_fkey',
            'emails',
            ['email_id'],
            ['id']
        )
