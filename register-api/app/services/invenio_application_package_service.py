from typing import Optional, Tuple
import os
import uuid
from datetime import datetime, timezone
import cwl_utils
import cwl_utils.parser
from sqlalchemy.orm import Session
from fastapi.logger import logger
from types import SimpleNamespace

from app.models.application_package import ApplicationPackageDetails
from app.models.application_package_version import ApplicationPackageVersion

from app.models.job import Job, JobStatus
from app.core.config import settings
from ap_validator.app_package import AppPackage
import schema_salad
import shutil
import yaml

from app.services.invenio_rdm_service import IvenioRDMService


class ApplicationPackageService:
    def __init__(self, db: Session, token: str):
        self.db = db
        self.token = token
        self.invenio_url = settings.RDM_URL
        
        logger.error("Initialized RDM Service with " + self.invenio_url )

    def validate_package(self, file_path: str) -> bool:
        """Validate the application package using the validator."""
        try:
            ap = AppPackage.from_url(file_path)
            result = ap.check_all(include=["error", "hint"])
            return result['valid'], result.get('issues', [])
        except schema_salad.exceptions.ValidationException as e:
            return False, [str(e)]

    def save_uploaded_file(self, namespace: str, jobId:str, file_content: bytes, filename: str) -> str:
        """Save the uploaded file to storage."""
        job_upload_dir = os.path.join(settings.STORAGE_PATH, namespace, jobId)
        os.makedirs(job_upload_dir, exist_ok=True)
        
        file_path = os.path.join(job_upload_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        return file_path
    
    def get_cwl_file_path(self, namespace, artifactName, version):
        package = self.get_package(namespace, artifactName, version)
        return package.cwl_url

    def quick_parse(self, namespace: str, jobId: str, filename: str) -> Tuple[str, str]:
        """Quick parse the uploaded file."""
        file_path = os.path.join(settings.STORAGE_PATH, namespace, jobId, filename)
        cwl_workflow, cwl_tool, cwl_metadata = self.parse_cwl_file(file_path)

        # the versions we're expecting contain a #workflow and #CommandLinetool in the uploaded CWL.
        if not cwl_workflow or not cwl_tool:
            raise ValueError("Invalid CWL file: missing workflow or tool definition")

        # Extract package information
        artifact_name = self._extract_artifact_name(cwl_workflow)
        artifact_version = self._extract_artifact_version(cwl_metadata)  # TODO: Implement version extraction

        return artifact_name, artifact_version

    def create_job(self, jobId: str, namespace: str, filename: str, artifact_name: str = None, artifact_version: str = None) -> Job:
        """Create a new job record."""
        job = Job(
            id=jobId,
            status=JobStatus.PENDING,
            message="Job queued for processing",
            progress=0,
            namespace=namespace,
            filename=filename,
            artifact_name=artifact_name,
            artifact_version=artifact_version
        )
        self.db.add(job)
        self.db.commit()
        return job

    def update_job_status(self, job_id: str, status: JobStatus, message: str, progress: int = 0) -> None:
        """Update job status and progress."""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.message = message
            job.progress = progress
            self.db.commit()

    def parse_cwl_file(self, file_path: str) -> Tuple[object, object, object]:
        """Parse CWL file and extract workflow and tool information."""
        cwl = cwl_utils.parser.load_document_by_uri(file_path, load_all=True)
        cwl_workflow = None
        cwl_tool = None
        extra_meta = None
        
        for x in cwl:
            logger.error(x)
            if "Workflow" in str(type(x)):
                logger.info(f"Found workflow: {x.id}")
                cwl_workflow = x
            if "CommandLineTool" in str(type(x)):
                logger.info(f"Found tool: {x.id}")
                cwl_tool = x

        # Only works on yaml?
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        extra_meta = self.dict_to_namespace(data)
        return cwl_workflow, cwl_tool, extra_meta

    def dict_to_namespace(self, data):
        if isinstance(data, dict):
            return SimpleNamespace(**{k: self.dict_to_namespace(v) for k, v in data.items()})
        elif isinstance(data, list):
            return [self.dict_to_namespace(item) for item in data]
        else:
            return data

    def extract_docker_image(self, cwl_tool: object) -> Optional[str]:
        """Extract docker image from CWL tool requirements."""
        reqs: list[any] = cwl_tool.requirements
        for req in reqs:
            if "DockerRequirement" in str(type(req)):
                return req.dockerPull
        return None

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
    

    def get_application_package_version(self,application_package: ApplicationPackageDetails, artifact_version: str):
        rdm_service = IvenioRDMService(self.invenio_url, self.token)
        version = rdm_service.get_package_version(application_package.namespace, application_package.artifactName, artifact_version)
        return version

    def update_or_create_version( self, 
                application_package: ApplicationPackageDetails,
                artifact_version: str,
                cwl_id: str,
                cwl_url: str ,
                docker_image: str,
                published=False,
                cwl_version: str =None,
                uploader:str = None,

            ) -> Tuple[ApplicationPackageVersion, bool]:
        
        """Get existing package or create a new one."""
        app_package_version = self.get_application_package_version(application_package,artifact_version )

        if app_package_version:
            # TODO, less generic exception
            if app_package_version.published:
                raise ValueError("Application version already exists and has been published!")

            # logger.error("App Package Version already exists")
            # if app_package_version.published:
            #     return app_package_version, False
            
            #TODO Update RDM with the new file

            # app_package_version.cwl_id = cwl_id
            # app_package_version.cwl_url = cwl_url
            # app_package_version.published = published
            # app_package_version.cwl_version = cwl_version
            # app_package_version.uploader = uploader
            # self.db.commit()
            return app_package_version, True
        else:   
            app_package_version = ApplicationPackageVersion(
                artifact_version = artifact_version,
                app_package =application_package,
                cwl_id = cwl_id,
                cwl_url = cwl_url,
                published = published,
                cwl_version = cwl_version,
                uploader = uploader
            )
            IvenioRDMService(self.invenio_url, self.token).add_package_version(app_package_version)


        return app_package_version, True


    def process_application_package(self, namespace: str, filename: str, job_id: str) -> None:
        """Process the uploaded application package."""
        try:
            self.update_job_status(job_id, JobStatus.PROCESSING, "Processing application package")
            
            # Parse CWL file and extract information
            file_path = os.path.join(settings.STORAGE_PATH, namespace, job_id, filename)
            cwl_workflow, cwl_tool, extra_metadata = self.parse_cwl_file(file_path)
            
            # the versions we're expecting contain a #workflow and #CommandLinetool in the uploaded CWL.
            if not cwl_workflow or not cwl_tool:
                raise ValueError("Invalid CWL file: missing workflow or tool definition")
            
            # Extract package information
            artifact_name = self._extract_artifact_name(cwl_workflow)
            docker_image = self.extract_docker_image(cwl_tool)
            artifact_version = self._extract_artifact_version(extra_metadata)  # TODO: Implement version extraction
            logger.error("processing {}:{}".format(artifact_name, artifact_version))
            
            final_dir = os.path.join(settings.STORAGE_PATH, namespace, artifact_name, artifact_version)
            os.makedirs(final_dir, exist_ok=True)
            dest_file_path = os.path.join(final_dir, filename)

            # Copy cwl to correct location
           


            shutil.copy(file_path, dest_file_path)


            # TODO 
            #new_image_path: str = self.pull_image(namespace, artifact_name, artifact_version, docker_image)

            # Create or update package
            package, created = self.get_or_create_package(
                namespace=namespace,
                artifact_name=artifact_name,
                job_id=job_id
            )

            # TODO store uploader information?
            try:
                package_version, version_created = self.update_or_create_version(
                    application_package = package,
                    artifact_version=artifact_version,
                    cwl_id=artifact_name,
                    cwl_url=dest_file_path,
                    docker_image=docker_image,
                    published=False,
                    cwl_version=None,
                    uploader=None,
                )
            except ValueError as e:
                self._handle_version_exists(job_id, package, artifact_version )
                return

            self._handle_successful_processing(job_id)

        except Exception as e:
            self._handle_processing_error(job_id, e)



    def _extract_artifact_name(self, cwl_workflow: object) -> str:
        """Extract artifact name from CWL workflow."""
        try:
            return cwl_workflow.id.split('#')[1]
        except (AttributeError, IndexError):
            raise ValueError("Invalid CWL workflow: missing or invalid ID")

    def _extract_artifact_version(self, cwl_meta: object) -> str:
        """Extract artifact version from CWL workflow."""
        # TODO: Implement proper version extraction from CWL metadata
        return cwl_meta.__getattribute__('s:softwareVersion')


    def _handle_version_exists(self, job_id: str, package: ApplicationPackageDetails, artifact_version: str) -> None:
        """Handle case where package version already exists."""
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"A Published Application package version with this namespace, name, and version already exists. {package.namespace}/{package.artifact_name}/{artifact_version}",
            100
        )

    def _handle_successful_processing(self, job_id: str) -> None:
        """Handle successful package processing."""
        self.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            "Application package processed successfully",
            100
        )

    def _handle_processing_error(self, job_id: str, error: Exception) -> None:
        """Handle package processing errors."""
        logger.error(f"Error processing application package: {str(error)}")
        logger.exception(error)
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"Error processing application package: {str(error)}"
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