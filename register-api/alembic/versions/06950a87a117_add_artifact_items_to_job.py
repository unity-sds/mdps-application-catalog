"""add artifact items to job

Revision ID: 06950a87a117
Revises: d1ca922f47dd
Create Date: 2025-04-16 13:52:34.841380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06950a87a117'
down_revision = 'd1ca922f47dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('artifact_name', sa.String()))
    op.add_column('jobs', sa.Column('artifact_version', sa.String()))


def downgrade() -> None:
    op.drop_column('jobs', 'artifact_name')
    op.drop_column('jobs', 'artifact_version')