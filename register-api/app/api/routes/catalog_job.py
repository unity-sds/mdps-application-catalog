from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from fastapi.security import HTTPAuthorizationCredentials
from app.core.database import get_db
from app.core.security import security
from app.models.catalog_job import CatalogJobStatus
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.job import Job

router = APIRouter()

@router.get("/{job_id}", response_model=CatalogJobStatus)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

def get_job_by_id(db: Session, job_id: str) -> Optional[CatalogJobStatus]:
    """
    Look up a job by its ID and return it as a CatalogJobStatus
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    return CatalogJobStatus.from_db_job(job) 