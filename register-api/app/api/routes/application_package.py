import json
import cwl_utils
import cwl_utils.parser
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials
import schema_salad
from app.core.security import security
from app.models.application_package import ApplicationPackageDetails, ApplicationPackageCreate
from app.models.application_package_db import ApplicationPackage
from datetime import datetime
import os
import uuid
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job, JobStatus

from app.models.catalog_job import CatalogJobResponse
from app.models.cwl import CWLUploadRequest
from app.models.publish import PublishResponse

from ap_validator.app_package import AppPackage


router = APIRouter()

async def process_application_package(db: Session, namespace: str, filename: str, job_id: str):
    """
    Background task to process the uploaded application package
    """
    try:
        # Update job status to processing
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = JobStatus.PROCESSING
        job.message = "Processing application package"
        job.progress = 0
        db.commit()
        
        # Parse CWL file
        file_path = os.path.join(settings.STORAGE_PATH, namespace, filename)
        cwl = cwl_utils.parser.load_document_by_uri(file_path, load_all=True)
        for x in cwl:
            if "Workflow" in str(type(x)):
                cwl_workflow = x
            if "CommandLineTool" in str(type(x)):
                cwl_tool = x
    

        # Extract information from CWL
        docker_image = None
        for req in cwl_tool.requirements or []:
            if "DockerRequirement" in str(type(req)):
                docker_image = req.dockerPull
                break

        #Version
        artifact_version = "1.0.0"
        
        # need to create or update appPackage based on namespace/artiface_name/artifact_version combo
        app_package = db.query(ApplicationPackage).filter(ApplicationPackage.namespace == namespace, ApplicationPackage.artifact_name == cwl_workflow.id.split('#')[1], ApplicationPackage.artifact_version == artifact_version).first()
        if app_package:
            if app_package.published:
                job.status = JobStatus.FAILED
                job.artifact_name=app_package.artifact_name
                job.artifact_version=app_package.artifact_version
                job.message = "A Published Application package with this namespace, name, and version already exists. ${app_package.namespace}/${app_package.artifact_name}/${app_package.artifact_version}"    
                job.progress = 100
                db.commit()
                return
            else:
                app_package.docker_image = docker_image
                app_package.cwl_url = f"/storage/{namespace}/{filename}"
                app_package.job_id = job_id
                db.commit()
        else:
            package = ApplicationPackage(
                id=str(uuid.uuid4()),
                namespace=namespace,
                artifact_name=cwl_workflow.id.split('#')[1],  
                artifact_version=artifact_version,  # TODO: Extract version from CWL or metadata
                cwl_id=cwl_workflow.id.split('#')[1],
                docker_image=docker_image,
                cwl_url=f"/storage/{namespace}/{filename}",
                job_id=job_id
             )
            db.add(package)
            db.commit()
        
        # Update progress
        job.progress = 50
        job.artifact_name=cwl_workflow.id.split('#')[1]
        job.artifact_version=artifact_version
        job.message = "CWL file parsed and package created"
        db.commit()
        
        # TODO: Add more processing steps here
        
        # Update final status
        job.status = JobStatus.COMPLETED
        job.message = "Application package processed successfully"
        job.progress = 100
        db.commit()
    except Exception as e:
        logger.error(f"Error processing application package: {str(e)}")
        job.status = JobStatus.FAILED
        job.message = f"Error processing application package: {str(e)}"
        job.progress = 0
        db.commit()

@router.post("/{namespace}/ogc-application-package", response_model=CatalogJobResponse)
async def register_application_package(
    namespace: str,
    request: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Create namespace directory if it doesn't exist
    namespace_dir = os.path.join(settings.STORAGE_PATH, namespace)
    os.makedirs(namespace_dir, exist_ok=True)
    
    # Save the uploaded file
    file_path = os.path.join(namespace_dir, request.filename)
    with open(file_path, "wb") as buffer:
        content = await request.read()
        buffer.write(content)
    
    try:
        ap = AppPackage.from_url(file_path)
        result = ap.check_all(include=["error", "hint"])
        if not result['valid']:
            raise HTTPException(status_code=400, detail="Invalid application package: " + json.dumps(result['issues']))
    except schema_salad.exceptions.ValidationException as e:
        raise HTTPException(status_code=400, detail=f"Unable to validate OGC Application Package: {str(e)}" )

    

    # Create job record
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        message="Job queued for processing",
        progress=0,
        namespace=namespace,
        filename=request.filename
    )
    db.add(job)
    db.commit()
    
    # Add background task
    background_tasks.add_task(
        process_application_package,
        db=db,
        namespace=namespace,
        filename=request.filename,
        job_id=job_id
    )
    
    return CatalogJobResponse(
        jobId=job_id,
        status="pending",
        message=f"Registration of {request.filename} initiated. Job ID: {job_id}"
    )

@router.get("/{namespace}/{artifactName}/{version}", response_model=ApplicationPackageDetails)
async def get_application_package_details(
    namespace: str,
    artifactName: str,
    version: str,
    db: Session = Depends(get_db)
):
    package = db.query(ApplicationPackage).filter(
        ApplicationPackage.namespace == namespace,
        ApplicationPackage.artifact_name == artifactName,
        ApplicationPackage.artifact_version == version
    ).first()
    
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    
    return ApplicationPackageDetails.from_db_package(package)

@router.post("/{namespace}/{artifactName}/{version}/publish", response_model=PublishResponse)
async def publish_application_package(
    namespace: str,
    artifactName: str,
    version: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    package = db.query(ApplicationPackage).filter(
        ApplicationPackage.namespace == namespace,
        ApplicationPackage.artifact_name == artifactName,
        ApplicationPackage.artifact_version == version
    ).first()
    
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    
    package.published = True
    package.published_date = datetime.now()
    db.commit()
    
    return PublishResponse(
        namespace=namespace,
        artifactName=artifactName,
        artifactVersion=version,
        published=True,
        message="Package published successfully"
    )

@router.post("/{namespace}/{artifactName}/{version}/unpublish", response_model=PublishResponse)
async def unpublish_application_package(
    namespace: str,
    artifactName: str,
    version: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    package = db.query(ApplicationPackage).filter(
        ApplicationPackage.namespace == namespace,
        ApplicationPackage.artifact_name == artifactName,
        ApplicationPackage.artifact_version == version
    ).first()
    
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    
    package.published = False
    package.published_date = None
    db.commit()
    
    return PublishResponse(
        namespace=namespace,
        artifactName=artifactName,
        artifactVersion=version,
        published=False,
        message="Package unpublished successfully"
    ) 