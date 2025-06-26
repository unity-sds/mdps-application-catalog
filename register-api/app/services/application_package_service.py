from typing import Optional, Tuple
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.logger import logger

from app.models.application_package_db import ApplicationPackage, ApplicationPackageVersion
from app.models.job import JobStatus
from app.services.base_application_package_service import BaseApplicationPackageService


class ApplicationPackageService(BaseApplicationPackageService):
    def __init__(self, db: Session):
        super().__init__(db)
    
    def get_cwl_file_path(self, namespace, artifactName, version):
        package = self.get_package(namespace, artifactName)
        return package.cwl_url

    def get_or_create_package(
        self, 
        namespace: str, 
        artifact_name: str, 
        job_id: str
    ) -> Tuple[ApplicationPackage, bool]:
        """Get existing package or create a new one."""
        app_package = self.db.query(ApplicationPackage).filter(
            ApplicationPackage.namespace == namespace,
            ApplicationPackage.artifact_name == artifact_name
        ).first()
        # we now have the application pacakge. We may need to create this version as well?

        if app_package:
            app_package.job_id = job_id
            self.db.commit()
            return app_package, False

        package = ApplicationPackage(
            id=str(uuid.uuid4()),
            namespace=namespace,
            artifact_name=artifact_name,
            job_id=job_id
        )
        self.db.add(package)
        self.db.commit()
        return package, True

    def get_application_package_version(self, application_package: ApplicationPackage, artifact_version: str):
        app_package_version = self.db.query(ApplicationPackageVersion).filter(
            ApplicationPackageVersion.application_package_id == application_package.id,
            ApplicationPackageVersion.artifact_version == artifact_version
        ).first()
        return app_package_version

    def update_or_create_version(self, 
                application_package: ApplicationPackage,
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
            # TODO, less generic exception
            if app_package_version.published:
                raise ValueError("Application version already exists and has been published!")

            logger.error("App Package Version already exists")
            if app_package_version.published:
                return app_package_version, False
            app_package_version.cwl_id = cwl_id
            app_package_version.cwl_url = cwl_url
            app_package_version.published = published
            app_package_version.cwl_version = cwl_version
            app_package_version.uploader = uploader
            self.db.commit()
            return app_package_version, True
        else:
            app_package_version = ApplicationPackageVersion(
                id=str(uuid.uuid4()),
                artifact_version=artifact_version,
                cwl_id=cwl_id,
                cwl_url=cwl_url,
                published=published,
                cwl_version=cwl_version,
                uploader=uploader,
                application_package_id=application_package.id
            )
        self.db.add(app_package_version)
        self.db.commit()
        return app_package_version, True


    def _handle_version_exists(self, job_id: str, package: ApplicationPackage, artifact_version: str) -> None:
        """Handle case where package version already exists."""
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"A Published Application package version with this namespace, name, and version already exists. {package.namespace}/{package.artifact_name}/{artifact_version}",
            100
        )

    def get_package(self, namespace: str, artifact_name: str) -> Optional[ApplicationPackage]:
        """List application package by namespace, name and version."""
        return self.db.query(ApplicationPackage).filter(
            ApplicationPackage.namespace == namespace,
            ApplicationPackage.artifact_name == artifact_name
        ).first()

    def list_packages(self, namespace: str, artifact_name: str) -> Optional[list[ApplicationPackage]]:       
        """Get application package by namespace, name and version."""
        # TODO add filtering
        return self.db.query(ApplicationPackage).all()


    #TODO - needs to update the _version_, not the _package_
    def update_package_version_publish_status(
        self, 
        artifact_version: ApplicationPackageVersion, 
        published: bool
    ) -> ApplicationPackage:
        """Update package publish status."""
        
        artifact_version.published = published
        artifact_version.published_date = datetime.now() if published else None
        self.db.commit()
        return artifact_version 
    

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