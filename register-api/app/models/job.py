from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    message = Column(String)
    progress = Column(Integer, default=0)
    namespace = Column(String)
    filename = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
    artifact_name = Column(String)
    artifact_version = Column(String)

    def __str__(self) -> str:
        """Return a string representation of the Job."""
        return (
            f"Job(id={self.id}, "
            f"status={self.status.value}, "
            f"progress={self.progress}%, "
            f"namespace={self.namespace}, "
            f"filename={self.filename}, "
            f"artifact={self.artifact_name or 'N/A'}:{self.artifact_version or 'N/A'}, "
            f"message={self.message or 'N/A'})"
        )