from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.application_package_db import ApplicationPackage

class ApplicationPackageDetails(BaseModel):
    namespace: str
    artifactName: str
    artifactVersion: str
    cwlId: str
    dateCreated: datetime
    dateUpdated: datetime
    published: bool
    description: Optional[str] = None
    uploader: Optional[str] = None
    publishedDate: Optional[datetime] = None
    sourceRepository: Optional[str] = None
    dockerImage: Optional[str] = None
    cwlUrl: Optional[str] = None

    @classmethod
    def from_db_package(cls, package: ApplicationPackage) -> 'ApplicationPackageDetails':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """
        return cls(
            namespace=package.namespace,
            artifactName=package.artifact_name,
            artifactVersion=package.artifact_version,
            cwlId=package.cwl_id,
            dateCreated=package.created_at,
            dateUpdated=package.updated_at or package.created_at,
            published=package.published,
            description=package.description,
            uploader=package.uploader,
            publishedDate=package.published_date,
            sourceRepository=package.source_repository,
            dockerImage=package.docker_image,
            cwlUrl=package.cwl_url,
        )

class ApplicationPackageCreate(BaseModel):
    namespace: str
    artifactName: str
    artifactVersion: str
    cwlId: str
    description: Optional[str] = None
    uploader: Optional[str] = None
    sourceRepository: Optional[str] = None
    dockerImage: Optional[str] = None
    cwlUrl: Optional[str] = None

    def to_db_package(self, job_id: str) -> ApplicationPackage:
        """
        Convert to a database ApplicationPackage model
        """
        return ApplicationPackage(
            namespace=self.namespace,
            artifact_name=self.artifactName,
            artifact_version=self.artifactVersion,
            cwl_id=self.cwlId,
            description=self.description,
            uploader=self.uploader,
            source_repository=self.sourceRepository,
            docker_image=self.dockerImage,
            cwl_url=self.cwlUrl,
            job_id=job_id
        ) 