from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CatalogJobResponse(BaseModel):
    jobId: str
    status: str
    message: Optional[str] = None

class CatalogJobStatus(BaseModel):
    jobId: str
    status: str
    namespace: Optional[str] = None
    artifactName: Optional[str] = None
    artifactVersion: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    message: Optional[str] = None
    errorDetails: Optional[str] = None
    catalogEntryUrl: Optional[str] = None 