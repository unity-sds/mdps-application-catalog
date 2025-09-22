from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.application_package_db import ApplicationPackage
from app.models.application_package_db import ApplicationPackageVersion as apv


class ApplicationPackageVersion(BaseModel):


    artifact_version: str
    app_package: Optional[object] = None
    cwl_id: Optional[str] = None
    cwl_version: Optional[str] = None
    uploader: Optional[str] = None
    cwl_url: Optional[str] = None
    id: Optional[str] = None
    published: bool
    

    @classmethod
    def from_db_package_version(cls, package_version: apv) -> 'ApplicationPackageVersion':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """
        return cls(
            artifact_version=package_version.artifact_version,
            cwl_id=package_version.cwl_id,
            cwl_version=package_version.cwl_version,
            uploader=package_version.uploader,
            cwl_url=package_version.cwl_url,
            published=package_version.published,
        )
    
    @classmethod
    def from_rdm_package_version(cls, package_version) -> 'ApplicationPackageVersion':
        """
        Create an ApplicationPackageDetails from a database ApplicationPackage model
        """

        # get CWL link
        cwl_link = None
        file_link = package_version['links']['files']
        file_dict = package_version['files']['entries']
        for k in file_dict:
            if k.endswith(".cwl"):
                cwl_link = file_link + "/" + k + "/content"

        return cls(
            artifact_version=package_version['metadata']['version'],
            #cwl_id=package_version.cwl_id,
            #cwl_version=package_version.cwl_version,
            # TODO update username
            uploader="TEST USER",
            cwl_url=cwl_link,
            published=package_version['is_published'],

        )