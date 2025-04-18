from typing import Optional, Tuple
import os
import uuid
from datetime import datetime
import cwl_utils
import cwl_utils.parser
from sqlalchemy.orm import Session
from fastapi.logger import logger

from app.models.application_package_db import ApplicationPackage
from app.models.job import Job, JobStatus
from app.core.config import settings
from ap_validator.app_package import AppPackage
import schema_salad

class ApplicationPackageService:
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

    def save_uploaded_file(self, namespace: str, file_content: bytes, filename: str) -> str:
        """Save the uploaded file to storage."""
        namespace_dir = os.path.join(settings.STORAGE_PATH, namespace)
        os.makedirs(namespace_dir, exist_ok=True)
        
        file_path = os.path.join(namespace_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        return file_path

    def quick_parse(self, namespace: str, filename: str) -> Tuple[str, str]:
        """Quick parse the uploaded file."""
        file_path = os.path.join(settings.STORAGE_PATH, namespace, filename)
        cwl_workflow, cwl_tool = self.parse_cwl_file(file_path)

        # the versions we're expecting contain a #workflow and #CommandLinetool in the uploaded CWL.
        if not cwl_workflow or not cwl_tool:
            raise ValueError("Invalid CWL file: missing workflow or tool definition")

        # Extract package information
        artifact_name = self._extract_artifact_name(cwl_workflow)
        artifact_version = self._extract_artifact_version(cwl_workflow)  # TODO: Implement version extraction

        return artifact_name, artifact_version

    def create_job(self, namespace: str, filename: str, artifact_name: str = None, artifact_version: str = None) -> Job:
        """Create a new job record."""
        job = Job(
            id=str(uuid.uuid4()),
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

    def parse_cwl_file(self, file_path: str) -> Tuple[object, object]:
        """Parse CWL file and extract workflow and tool information."""
        cwl = cwl_utils.parser.load_document_by_uri(file_path, load_all=True)
        cwl_workflow = None
        cwl_tool = None
        
        for x in cwl:
            if "Workflow" in str(type(x)):
                logger.info(f"Found workflow: {x.id}")
                cwl_workflow = x
            if "CommandLineTool" in str(type(x)):
                logger.info(f"Found tool: {x.id}")
                cwl_tool = x
        
        return cwl_workflow, cwl_tool

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
        artifact_version: str,
        docker_image: str,
        cwl_url: str,
        job_id: str
    ) -> Tuple[ApplicationPackage, bool]:
        """Get existing package or create a new one."""
        app_package = self.db.query(ApplicationPackage).filter(
            ApplicationPackage.namespace == namespace,
            ApplicationPackage.artifact_name == artifact_name,
            ApplicationPackage.artifact_version == artifact_version
        ).first()

        if app_package:
            if app_package.published:
                return app_package, False
            app_package.docker_image = docker_image
            app_package.cwl_url = cwl_url
            app_package.job_id = job_id
            self.db.commit()
            return app_package, True

        package = ApplicationPackage(
            id=str(uuid.uuid4()),
            namespace=namespace,
            artifact_name=artifact_name,
            artifact_version=artifact_version,
            cwl_id=artifact_name,
            docker_image=docker_image,
            cwl_url=cwl_url,
            job_id=job_id
        )
        self.db.add(package)
        self.db.commit()
        return package, True


    def process_application_package(self, namespace: str, filename: str, job_id: str) -> None:
        """Process the uploaded application package."""
        try:
            self.update_job_status(job_id, JobStatus.PROCESSING, "Processing application package")
            
            # Parse CWL file and extract information
            file_path = os.path.join(settings.STORAGE_PATH, namespace, filename)
            cwl_workflow, cwl_tool = self.parse_cwl_file(file_path)
            
            # the versions we're expecting contain a #workflow and #CommandLinetool in the uploaded CWL.
            if not cwl_workflow or not cwl_tool:
                raise ValueError("Invalid CWL file: missing workflow or tool definition")
            
            # Extract package information
            artifact_name = self._extract_artifact_name(cwl_workflow)
            docker_image = self.extract_docker_image(cwl_tool)
            artifact_version = self._extract_artifact_version(cwl_workflow)  # TODO: Implement version extraction
            


            # Create or update package
            package, created = self.get_or_create_package(
                namespace=namespace,
                artifact_name=artifact_name,
                artifact_version=artifact_version,
                docker_image=docker_image,
                cwl_url=f"/storage/{namespace}/{filename}",
                job_id=job_id
            )

            if not created:
                self._handle_package_exists(job_id, package)
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

    def _extract_artifact_version(self, cwl_workflow: object) -> str:
        """Extract artifact version from CWL workflow."""
        # TODO: Implement proper version extraction from CWL metadata
        return "1.0.0"

    def _handle_package_exists(self, job_id: str, package: ApplicationPackage) -> None:
        """Handle case where package already exists."""
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"A Published Application package with this namespace, name, and version already exists. {package.namespace}/{package.artifact_name}/{package.artifact_version}",
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
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            f"Error processing application package: {str(error)}"
        )

    def get_package(self, namespace: str, artifact_name: str, version: str) -> Optional[ApplicationPackage]:
        """Get application package by namespace, name and version."""
        return self.db.query(ApplicationPackage).filter(
            ApplicationPackage.namespace == namespace,
            ApplicationPackage.artifact_name == artifact_name,
            ApplicationPackage.artifact_version == version
        ).first()

    def update_package_publish_status(
        self, 
        namespace: str, 
        artifact_name: str, 
        version: str, 
        published: bool
    ) -> ApplicationPackage:
        """Update package publish status."""
        package = self.get_package(namespace, artifact_name, version)
        if not package:
            raise ValueError("Application package not found")
        
        package.published = published
        package.published_date = datetime.now() if published else None
        self.db.commit()
        return package 