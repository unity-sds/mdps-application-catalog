from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.application_package_db import ApplicationPackage


from app.models.application_package_version import ApplicationPackageVersion

class ApplicationPackageDetails(BaseModel):
    namespace: str
    artifactName: str
    dateCreated: datetime
    dateUpdated: datetime
    description: Optional[str] = None
    sourceRepository: Optional[str] = None
    dockerImage: Optional[str] = None
    versions: List[ApplicationPackageVersion] = []
    id: Optional[str] =  None

    @classmethod
    def from_db_package(cls, package: ApplicationPackage) -> 'ApplicationPackageDetails':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """
        return cls(
            namespace=package.namespace,
            artifactName=package.artifact_name,
            dateCreated=package.created_at,
            dateUpdated=package.updated_at or package.created_at,
            description=package.description,
            sourceRepository=package.source_repository,
            dockerImage=package.docker_image
        )
    
    @classmethod
    def from_db_package_with_versions(cls, package: ApplicationPackage) -> 'ApplicationPackageDetails':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """
        return cls(
            namespace=package.namespace,
            artifactName=package.artifact_name,
            dateCreated=package.created_at,
            dateUpdated=package.updated_at or package.created_at,
            description=package.description,
            sourceRepository=package.source_repository,
            dockerImage=package.docker_image,
            versions=[ApplicationPackageVersion.from_db_package_version(version) for version in package.versions]
        )
    
    @classmethod
    def from_rdm_package(cls, package) -> 'ApplicationPackageDetails':
        """
        create an application pacakge from RDM
        """
        return cls(
            namespace=package['parent']['communities']['entries'][0]['slug'],
            artifactName=package['metadata']['title'],
            dateCreated=package['created'],
            dateUpdated=package['updated'],
            description=package['metadata']['description'],
            sourceRepository=package['custom_fields']['mdps:software_repository_url'],
            dockerImage=None,
            id=package['id']
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