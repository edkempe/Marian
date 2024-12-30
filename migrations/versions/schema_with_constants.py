"""Initial schema with constants.

Revision ID: schema_with_constants
Revises: None
Create Date: 2024-12-29 23:25:33.000000

This migration creates the initial schema for all tables using constants from shared_lib.schema_constants.
"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op

from shared_lib.schema_constants import COLUMN_SIZES, EmailDefaults, AnalysisDefaults, LabelDefaults

# revision identifiers, used by Alembic
revision = "schema_with_constants"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial schema for all tables."""
    # Create emails table
    op.create_table(
        "emails",
        sa.Column("id", sa.String(COLUMN_SIZES["EMAIL_ID"]), nullable=False),
        sa.Column("subject", sa.String(COLUMN_SIZES["EMAIL_SUBJECT"]), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("sender", sa.String(COLUMN_SIZES["EMAIL_FROM"]), nullable=True),
        sa.Column("to_address", sa.String(COLUMN_SIZES["EMAIL_TO"]), nullable=True),
        sa.Column("received_date", sa.DateTime(), nullable=True),
        sa.Column("labels", sa.String(COLUMN_SIZES["EMAIL_LABELS"]), nullable=True),
        sa.Column("threadId", sa.String(COLUMN_SIZES["EMAIL_THREAD_ID"]), nullable=True),
        sa.Column("has_attachments", sa.Boolean(), nullable=True),
        sa.Column("cc_address", sa.Text(), server_default=EmailDefaults.cc_address),
        sa.Column("bcc_address", sa.Text(), server_default=EmailDefaults.bcc_address),
        sa.Column("full_api_response", sa.Text(), server_default=EmailDefaults.api_response),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create email_analysis table
    op.create_table(
        "email_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email_id", sa.String(COLUMN_SIZES["EMAIL_ID"]), nullable=False),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("importance_score", sa.Float(), nullable=True),
        sa.Column("urgency_score", sa.Float(), nullable=True),
        sa.Column("category", sa.String(COLUMN_SIZES["ANALYSIS_CATEGORY"]), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_points", sa.Text(), server_default=AnalysisDefaults.summary),
        sa.Column("action_items", sa.Text(), server_default=AnalysisDefaults.summary),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create gmail_labels table
    op.create_table(
        "gmail_labels",
        sa.Column("id", sa.String(COLUMN_SIZES["LABEL_ID"]), nullable=False),
        sa.Column("name", sa.String(COLUMN_SIZES["LABEL_NAME"]), nullable=False),
        sa.Column("message_list_visibility", sa.String(COLUMN_SIZES["LABEL_TYPE"]), nullable=True),
        sa.Column("label_list_visibility", sa.String(COLUMN_SIZES["LABEL_TYPE"]), nullable=True),
        sa.Column("type", sa.String(COLUMN_SIZES["LABEL_TYPE"]), nullable=True),
        sa.Column("messages_total", sa.Integer(), nullable=True),
        sa.Column("messages_unread", sa.Integer(), nullable=True),
        sa.Column("threads_total", sa.Integer(), nullable=True),
        sa.Column("threads_unread", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(COLUMN_SIZES["LABEL_TYPE"]), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    """Drop all tables."""
    op.drop_table("email_analysis")
    op.drop_table("gmail_labels")
    op.drop_table("emails")
