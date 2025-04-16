from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.job import Job, JobStatus

class CatalogJobResponse(BaseModel):
    jobId: str
    status: str
    message: Optional[str] = None
    progress: Optional[int] = None

class CatalogJobStatus(BaseModel):
    jobId: str
    status: str
    namespace: str
    artifact_name: str
    artifact_version: str
    filename: str
    createdAt: datetime
    updatedAt: datetime
    message: Optional[str] = None
    progress: Optional[int] = None
    errorDetails: Optional[str] = None
    catalogEntryUrl: Optional[str] = None

    @classmethod
    def from_db_job(cls, job: Job) -> 'CatalogJobStatus':
        """
        Create a CatalogJobStatus from a database Job model
        """
        return cls(
            jobId=job.id,
            status=job.status.value,
            namespace=job.namespace,
            filename=job.filename,
            artifact_name=job.artifact_name,
            artifact_version=job.artifact_version,
            createdAt=job.created_at,
            updatedAt=job.updated_at or job.created_at,
            message=job.message,
            progress=job.progress
        )