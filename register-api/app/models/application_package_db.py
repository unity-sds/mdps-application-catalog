from pydantic import ConfigDict
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import json

# Association table for tags
application_package_tags = Table(
    'application_package_tags',
    Base.metadata,
    Column('application_package_id', String, ForeignKey('application_packages.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class ApplicationPackage(Base):
    
    __tablename__ = "application_packages"

    id = Column(String, primary_key=True, index=True)
    namespace = Column(String, index=True)
    artifact_name = Column(String, index=True)
    description = Column(String, nullable=True)
    source_repository = Column(String, nullable=True)
    docker_image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_id = Column(String, ForeignKey('jobs.id'))
    job = relationship("Job", back_populates="application_package")
    tags = relationship("Tag", secondary=application_package_tags, back_populates="application_packages")
    versions = relationship("ApplicationPackageVersion", back_populates="application_package", cascade="all, delete-orphan")

class ApplicationPackageVersion(Base):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    __tablename__ = "application_package_versions"

    id = Column(String, primary_key=True, index=True)
    artifact_version = Column(String, index=True)
    cwl_id = Column(String)
    cwl_version = Column(String, nullable=True)
    uploader = Column(String, nullable=True)
    cwl_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    published_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to ApplicationPackage
    application_package_id = Column(String, ForeignKey('application_packages.id'))
    application_package = relationship("ApplicationPackage", back_populates="versions")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    application_packages = relationship("ApplicationPackage", secondary=application_package_tags, back_populates="tags")

# Update the Job model to include relationship with ApplicationPackage
from app.models.job import Job
Job.application_package = relationship("ApplicationPackage", back_populates="job", uselist=False) 