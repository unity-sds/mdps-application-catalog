from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    tags: Optional[List[str]] = None 