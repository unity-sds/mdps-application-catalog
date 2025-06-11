from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.application_package_db import ApplicationPackage
from app.models.application_package_db import ApplicationPackageVersion as apv


class ApplicationPackageVersion(BaseModel):

    artifactVersion: str
    cwlId: Optional[str] = None
    cwlVersion: Optional[str] = None
    uploader: Optional[str] = None
    cwlUrl: Optional[str] = None
    published: bool

    @classmethod
    def from_db_package_version(cls, package_version: apv) -> 'ApplicationPackageVersion':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """
        return cls(
            artifactVersion=package_version.artifact_version,
            cwlId=package_version.cwl_id,
            cwlVersion=package_version.cwl_version,
            uploader=package_version.uploader,
            cwlUrl=package_version.cwl_url,
            published=package_version.published,
        )