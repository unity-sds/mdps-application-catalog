from typing import Optional, Tuple
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.logger import logger

from app.models.application_package import ApplicationPackageDetails
from app.models.application_package_version import ApplicationPackageVersion
from app.core.config import settings
from app.models.job import JobStatus
from app.services.invenio_rdm_service import IvenioRDMService
from app.services.base_application_package_service import BaseApplicationPackageService


class ApplicationPackageService(BaseApplicationPackageService):
    def __init__(self, db: Session, token: str):
        super().__init__(db)
        self.token = token
        self.invenio_url = settings.RDM_URL
        
        logger.error("Initialized RDM Service with " + self.invenio_url)
    
    def get_cwl_file_path(self, namespace, artifactName, version):
        package = self.get_package(namespace, artifactName)
        return package.cwl_url

    def get_or_create_package(
        self, 
        namespace: str, 
        artifact_name: str, 
        job_id: str
    ) -> Tuple[ApplicationPackageDetails, bool]:
        
        rdm_service = IvenioRDMService(self.invenio_url, self.token)
        app_package = rdm_service.get_package(namespace, artifact_name)
        if app_package:
            return app_package, False
        

        # Not saved until we create the version as well.
        return ApplicationPackageDetails(namespace=namespace, artifactName=artifact_name, dateUpdated=datetime.now(timezone.utc).isoformat(), dateCreated=datetime.now(timezone.utc).isoformat()), True
    

    def get_application_package_version(self, application_package: ApplicationPackageDetails, artifact_version: str):
        rdm_service = IvenioRDMService(self.invenio_url, self.token)
        version = rdm_service.get_package_version(application_package.namespace, application_package.artifactName, artifact_version)
        return version

    def update_or_create_version(self, 
                application_package: ApplicationPackageDetails,
                artifact_version: str,
                cwl_id: str,
                cwl_url: str,
                docker_image: str,
                published=False,
                cwl_version: str = None,
                uploader: str = None,

            ) -> Tuple[ApplicationPackageVersion, bool]:
        
        """Get existing package or create a new one."""
        app_package_version = self.get_application_package_version(application_package, artifact_version)

        if app_package_version:
            if app_package_version.published:
                logger.error(f"{application_package.artifactName}/")
                if artifact_version != "develop":
                    raise ValueError("Application version already exists and has been published!")

        app_package_version = ApplicationPackageVersion(
            artifact_version=artifact_version,
            app_package=application_package,
            cwl_id=cwl_id,
            cwl_url=cwl_url,
            published=published,
            cwl_version=cwl_version,
            uploader=uploader
        )
        IvenioRDMService(self.invenio_url, self.token).add_package_version(app_package_version)

        return app_package_version, True


    def _handle_version_exists(self, job_id: str, package: ApplicationPackageDetails, artifact_version: str) -> None:
        """Handle case where package version already exists."""
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"A Published Application package version with this namespace, name, and version already exists. {package.namespace}/{package.artifactName}/{artifact_version}",
            100
        )

    def get_package(self, namespace: str, artifact_name: str) -> Optional[ApplicationPackageDetails]:
        return IvenioRDMService(self.invenio_url, self.token).get_package(namespace=namespace, package_name=artifact_name)

        

    # def list_packages(self, namespace: str, artifact_name: str) -> Optional[list[ApplicationPackage]]:       
    #     """Get application package by namespace, name and version."""
    #     # TODO add filtering
    #     return self.db.query(ApplicationPackage).all()


    # #TODO - needs to update the _version_, not the _package_
    # def update_package_version_publish_status(
    #     self, 
    #     artifact_version: ApplicationPackageVersion, 
    #     published: bool
    # ) -> ApplicationPackage:
    #     """Update package publish status."""
        
    #     artifact_version.published = published
    #     artifact_version.published_date = datetime.now() if published else None
    #     self.db.commit()
    #     return artifact_version 
    

    #             new_image_path: str = self.pull_image(namespace, artifact_name, artifact_version, docker_image)

    # def pull_image(self, namespace, artifact_name, artifact_version, cwl_image_name: str)-> str:
    #     # aws ecr get-login-password --region us-west-2 | skopeo login --username AWS --password-stdin 237868187491.dkr.ecr.us-west-2.amazonaws.com
    #     # Login Succeeded!
    #     # skopeo copy  --override-os linux --override-arch amd64 docker://python:latest docker://237868187491.dkr.ecr.us-west-2.amazonaws.com/gangl/python:latest 
    #     dest_registry: str = settings.DESTINATION_REGISTRY
    #     try:
    #         # login to ECR 
    #         # create repo if it doesn't exist
    #         # Create new docker repo name
    #         dest_image = f"{dest_registry}/{namespace}/{artifact_name}/{artifact_version}"
    #         # copy docker container
            
    #         logger.info(f"Image {dest_image} pulled successfully.")
    #     # except podman.errors.APIError as e:
    #     #     logger.error(f"Error pulling image: {e}")
    #     #     raise Exception(f"Error pulling image: {e}")
    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred: {e}")
    #         raise Exception(f"An unexpected error occurred: {e}")
    #     finally:
    #         if 'client' in locals():
    #             client.close()