"""
Migration to add qualification field to users table
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_qualification_field'
down_revision = 'add_slugs'
branch_labels = None
depends_on = None

def upgrade():
    """Add qualification column to users table"""
    op.add_column('users', sa.Column('qualification', sa.String(100), nullable=True))

def downgrade():
    """Remove qualification column from users table"""
    op.drop_column('users', 'qualification') 