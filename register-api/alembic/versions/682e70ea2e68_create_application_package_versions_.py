"""create application package versions table

Revision ID: 682e70ea2e68
Revises: 
Create Date: 2024-03-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '682e70ea2e68'
down_revision = '8f5482000550' # Update this to the previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Create the new application_package_versions table
    op.create_table(
        'application_package_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('artifact_version', sa.String(), nullable=True),
        sa.Column('cwl_id', sa.String(), nullable=True),
        sa.Column('cwl_version', sa.String(), nullable=True),
        sa.Column('uploader', sa.String(), nullable=True),
        sa.Column('cwl_url', sa.String(), nullable=True),
        sa.Column('published', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('published_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_package_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['application_package_id'], ['application_packages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_package_versions_artifact_version'), 'application_package_versions', ['artifact_version'], unique=False)
    op.create_index(op.f('ix_application_package_versions_id'), 'application_package_versions', ['id'], unique=False)

    # Migrate data from application_packages to application_package_versions
    op.execute("""
        INSERT INTO application_package_versions (
            id,
            artifact_version,
            cwl_id,
            cwl_version,
            uploader,
            cwl_url,
            published,
            published_date,
            application_package_id,
            created_at,
            updated_at
        )
        SELECT 
            application_packages.id || '_v1',  -- Generate a unique ID for the version
            artifact_version,
            cwl_id,
            cwl_version,
            uploader,
            cwl_url,
            published,
            published_date,
            id,  -- This is the application_package_id
            created_at,
            updated_at
        FROM application_packages
        WHERE artifact_version IS NOT NULL
           OR cwl_id IS NOT NULL
           OR cwl_version IS NOT NULL
           OR uploader IS NOT NULL
           OR cwl_url IS NOT NULL
           OR published IS NOT NULL
           OR published_date IS NOT NULL
    """)

    # Drop the columns from application_packages
    op.drop_column('application_packages', 'artifact_version')
    op.drop_column('application_packages', 'cwl_id')
    op.drop_column('application_packages', 'cwl_version')
    op.drop_column('application_packages', 'uploader')
    op.drop_column('application_packages', 'cwl_url')
    op.drop_column('application_packages', 'published')
    op.drop_column('application_packages', 'published_date')

def downgrade():
    # Add the columns back to application_packages
    op.add_column('application_packages', sa.Column('published_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('application_packages', sa.Column('published', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('application_packages', sa.Column('cwl_url', sa.String(), nullable=True))
    op.add_column('application_packages', sa.Column('uploader', sa.String(), nullable=True))
    op.add_column('application_packages', sa.Column('cwl_version', sa.String(), nullable=True))
    op.add_column('application_packages', sa.Column('cwl_id', sa.String(), nullable=True))
    op.add_column('application_packages', sa.Column('artifact_version', sa.String(), nullable=True))

    # Migrate data back from application_package_versions to application_packages
    op.execute("""
        UPDATE application_packages ap
        SET 
            artifact_version = apv.artifact_version,
            cwl_id = apv.cwl_id,
            cwl_version = apv.cwl_version,
            uploader = apv.uploader,
            cwl_url = apv.cwl_url,
            published = apv.published,
            published_date = apv.published_date
        FROM application_package_versions apv
        WHERE ap.id = apv.application_package_id
    """)

    # Drop the application_package_versions table
    op.drop_index(op.f('ix_application_package_versions_id'), table_name='application_package_versions')
    op.drop_index(op.f('ix_application_package_versions_artifact_version'), table_name='application_package_versions')
    op.drop_table('application_package_versions') 