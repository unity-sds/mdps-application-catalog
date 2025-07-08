from typing import Optional, Tuple
import os
import uuid
from datetime import datetime
import cwl_utils
import cwl_utils.parser
from sqlalchemy.orm import Session
from fastapi.logger import logger
from types import SimpleNamespace

from app.models.job import Job, JobStatus
from app.core.config import settings
from ap_validator.app_package import AppPackage
import schema_salad
import shutil
import yaml


class BaseApplicationPackageService:
    def __init__(self, db: Session):
        self.db = db

    def validate_package(self, file_path: str) -> bool:
        """Validate the application package using the validator."""
        try:
            ap = AppPackage.from_url(file_path)
            result = ap.check_all(include=["error", "hint"])
            return result['valid'], result.get('issues', [])
        except schema_salad.exceptions.ValidationException as e:
            return False, [str(e)]

    def save_uploaded_file(self, namespace: str, jobId: str, file_content: bytes, filename: str) -> str:
        """Save the uploaded file to storage."""
        job_upload_dir = os.path.join(settings.STORAGE_PATH, namespace, jobId)
        os.makedirs(job_upload_dir, exist_ok=True)
        
        file_path = os.path.join(job_upload_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        return file_path

    def quick_parse(self, namespace: str, jobId: str, filename: str) -> Tuple[str, str]:
        """Quick parse the uploaded file."""
        file_path = os.path.join(settings.STORAGE_PATH, namespace, jobId, filename)
        cwl_workflow, cwl_tool, cwl_metadata = self.parse_cwl_file(file_path)

        # the versions we're expecting contain a #workflow and #CommandLinetool in the uploaded CWL.
        if not cwl_workflow or not cwl_tool:
            raise ValueError("Invalid CWL file: missing workflow or tool definition")

        # Extract package information
        artifact_name = self._extract_artifact_name(cwl_workflow)
        artifact_version = self._extract_artifact_version(cwl_metadata)

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
            logger.debug(x)
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

    def _extract_artifact_name(self, cwl_workflow: object) -> str:
        """Extract artifact name from CWL workflow."""
        try:
            return cwl_workflow.id.split('#')[1]
        except (AttributeError, IndexError):
            raise ValueError("Invalid CWL workflow: missing or invalid ID")

    def _extract_artifact_version(self, cwl_meta: object) -> str:
        """Extract artifact version from CWL workflow."""
        return cwl_meta.__getattribute__('s:softwareVersion')

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
            artifact_version = self._extract_artifact_version(extra_metadata)
            logger.debug("processing {}:{}".format(artifact_name, artifact_version))
            
            final_dir = os.path.join(settings.STORAGE_PATH, namespace, artifact_name, artifact_version)
            os.makedirs(final_dir, exist_ok=True)
            dest_file_path = os.path.join(final_dir, filename)

            shutil.copy(file_path, dest_file_path)

            # Create or update package
            package, created = self.get_or_create_package(
                namespace=namespace,
                artifact_name=artifact_name,
                job_id=job_id
            )

            try:
                package_version, version_created = self.update_or_create_version(
                    application_package=package,
                    artifact_version=artifact_version,
                    cwl_id=artifact_name,
                    cwl_url=dest_file_path,
                    docker_image=docker_image,
                    published=False,
                    cwl_version=None,
                    uploader=None,
                )
            except ValueError as e:
                self._handle_version_exists(job_id, package, artifact_version)
                return

            self._handle_successful_processing(job_id)

        except Exception as e:
            self._handle_processing_error(job_id, e)

    # Abstract methods to be implemented by subclasses
    def get_or_create_package(self, namespace: str, artifact_name: str, job_id: str):
        raise NotImplementedError("Subclasses must implement get_or_create_package")

    def get_application_package_version(self, application_package, artifact_version: str):
        raise NotImplementedError("Subclasses must implement get_application_package_version")

    def update_or_create_version(self, application_package, artifact_version: str, cwl_id: str, 
                                cwl_url: str, docker_image: str, published=False, cwl_version: str = None, 
                                uploader: str = None):
        raise NotImplementedError("Subclasses must implement update_or_create_version")

    def get_package(self, namespace: str, artifact_name: str):
        raise NotImplementedError("Subclasses must implement get_package")

    def _handle_version_exists(self, job_id: str, package, artifact_version: str):
        raise NotImplementedError("Subclasses must implement _handle_version_exists")

    def get_cwl_file_path(self, namespace, artifactName, version):
        raise NotImplementedError("Subclasses must implement get_cwl_file_path")