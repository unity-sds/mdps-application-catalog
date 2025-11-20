# my_repository/cli.py (or whatever your package name is)

import tempfile
import click
from flask.cli import with_appcontext

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity

@click.group()
def utilities():
    """Custom utility commands for this instance."""
    pass

@utilities.command('load-demo')
@with_appcontext
def load_demo_files():
    """Create a demo record with an attached file."""
    
    click.echo("Creating demo record...")

    # 1. Define metadata
    data = {
        "access": {
            "record": "public",
            "files": "public"
        },
        "custom_fields": {
            "mdps:software_repository_url": "https://github.com/unity-sds/unity-example-application",
        },
        "files": {
            "enabled": True
        },
        "metadata": {
            "title": "Example Application",
            "description": "Example application illustrating structure for MDPS App Generator application repositories",
            "resource_type": {
                "id": "ogc-application-package"
            },
            "publication_date": "2025-11-20",
            "creators": [{
                "person_or_org": {
                    "name": "Jet Propulsion Laboratory",
                    "type": "organizational",
                }
            }],
            "publisher": "ogc-app-catalog"
        }
    }

    # 2. Create draft
    draft = current_rdm_records_service.create(system_identity, data)

    # 3. File Setup
    record_filename = "ogc-app-package.cwl"

    # Initialize
    current_rdm_records_service.draft_files.init_files(
        system_identity, draft.id, data=[{'key': record_filename}]
    )

    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as tmp_file_stream:

        # Upload
        current_rdm_records_service.draft_files.set_file_content(
            system_identity, draft.id, record_filename, tmp_file_stream
        )

    # Commit
    current_rdm_records_service.draft_files.commit_file(
        system_identity, draft.id, record_filename
    )

    # 4. Publish
    record = current_rdm_records_service.publish(system_identity, draft.id)
    
    click.secho(f"Success! Record created with ID: {record.id}", fg="green")