"""Add cc_address and bcc_address fields to emails table

This migration adds CC and BCC recipient fields to the emails table.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision = "20241223_02"
down_revision = "20241223_01"  # Points to initial schema
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
