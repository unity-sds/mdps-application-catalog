"""add artifactname

Revision ID: 31555e306c49
Revises: 06950a87a117
Create Date: 2025-04-16 14:05:49.063357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31555e306c49'
down_revision = '06950a87a117'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('artifact_name', sa.String()))
    op.add_column('jobs', sa.Column('artifact_version', sa.String()))


def downgrade() -> None:
    op.drop_column('jobs', 'artifact_name')
    op.drop_column('jobs', 'artifact_version')