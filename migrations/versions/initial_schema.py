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
        sa.Column('cc_address', sa.Text(), server_default="''''''"),
        sa.Column('bcc_address', sa.Text(), server_default="''''''"),
        sa.PrimaryKeyConstraint('id')
    )

    # Create email_analysis table
    op.create_table(
        'email_analysis',
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('analysis_date', sa.DateTime(), nullable=True),
        sa.Column('analyzed_date', sa.DateTime(), nullable=False),
        sa.Column('prompt_version', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('category', sa.Text(), nullable=False),
        sa.Column('priority_score', sa.Integer(), nullable=False),
        sa.Column('priority_reason', sa.Text(), nullable=False),
        sa.Column('action_needed', sa.Boolean(), nullable=False),
        sa.Column('action_type', sa.Text(), nullable=False),
        sa.Column('action_deadline', sa.Text(), nullable=True),
        sa.Column('key_points', sa.Text(), nullable=False),
        sa.Column('people_mentioned', sa.Text(), nullable=False),
        sa.Column('links_found', sa.Text(), nullable=False),
        sa.Column('links_display', sa.Text(), nullable=False),
        sa.Column('project', sa.Text(), nullable=True),
        sa.Column('topic', sa.Text(), nullable=True),
        sa.Column('ref_docs', sa.Text(), nullable=True),
        sa.Column('sentiment', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('email_id')
    )

    # Create gmail_labels table
    op.create_table(
        'gmail_labels',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('archived_date', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.Integer(), nullable=False),
        sa.Column('modified_date', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tags_name', 'tags', [sa.text('name COLLATE NOCASE')])
    op.create_index('idx_tags_deleted', 'tags', ['deleted'])

    # Create catalog_items table
    op.create_table(
        'catalog_items',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(2000), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('archived_date', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.Integer(), nullable=False),
        sa.Column('modified_date', sa.Integer(), nullable=False),
        sa.Column('item_info', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_catalog_items_deleted', 'catalog_items', ['deleted'])
    op.create_index('idx_catalog_items_status', 'catalog_items', ['status'])
    op.create_index('idx_catalog_items_title', 'catalog_items', ['title'])

    # Create catalog_tags table
    op.create_table(
        'catalog_tags',
        sa.Column('catalog_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['catalog_id'], ['catalog_items.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id']),
        sa.PrimaryKeyConstraint('catalog_id', 'tag_id')
    )

    # Create item_relationships table
    op.create_table(
        'item_relationships',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('created_date', sa.Integer(), nullable=False),
        sa.Column('relationship_info', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['catalog_items.id']),
        sa.ForeignKeyConstraint(['target_id'], ['catalog_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_relationships_source', 'item_relationships', ['source_id'])
    op.create_index('idx_relationships_target', 'item_relationships', ['target_id'])
    op.create_index('idx_relationships_type', 'item_relationships', ['relationship_type'])

    # Create asset_catalog_items table
    op.create_table(
        'asset_catalog_items',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('asset_id', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create asset_catalog_tags table
    op.create_table(
        'asset_catalog_tags',
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['asset_catalog_items.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id']),
        sa.PrimaryKeyConstraint('asset_id', 'tag_id')
    )

    # Create asset_dependencies table
    op.create_table(
        'asset_dependencies',
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('dependency_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['asset_catalog_items.id']),
        sa.ForeignKeyConstraint(['target_id'], ['asset_catalog_items.id']),
        sa.PrimaryKeyConstraint('source_id', 'target_id')
    )


def downgrade() -> None:
    op.drop_table('asset_dependencies')
    op.drop_table('asset_catalog_tags')
    op.drop_table('asset_catalog_items')
    op.drop_table('item_relationships')
    op.drop_table('catalog_tags')
    op.drop_table('catalog_items')
    op.drop_table('tags')
    op.drop_table('gmail_labels')
    op.drop_table('email_analysis')
    op.drop_table('emails')
