from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.application_package import ApplicationPackageDetails

class ApplicationPackageSummary(BaseModel):
    namespace: str
    artifactName: str
    artifactVersion: str
    dateCreated: datetime
    published: bool
    description: Optional[str] = None
    publishedDate: Optional[datetime] = None
    uploader: Optional[str] = None
    tags: Optional[List[str]] = None
    detailsUrl: Optional[str] = None

class PackageDiscoveryResponse(BaseModel):
    total: int
    page: int
    limit: int
    packages: List[ApplicationPackageDetails] 