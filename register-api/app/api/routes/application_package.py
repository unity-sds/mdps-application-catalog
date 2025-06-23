import json
from typing import Annotated
import cwl_utils
import cwl_utils.parser
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.logger import logger
from fastapi.security import HTTPAuthorizationCredentials
import schema_salad
from app.core.auth.jwt_authorizer import JWTAuthorizer
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
from app.services.application_package_service import ApplicationPackageService
from app.services.invenio_application_package_service import ApplicationPackageService as InvenioApplicationPackageService

import app.core.auth.auth as app_auth
from starlette.status import HTTP_401_UNAUTHORIZED
    

router = APIRouter()

authorizer = app_auth.get_authorizer()

@router.post("/{namespace}/ogc-application-package", response_model=CatalogJobResponse)
async def register_application_package(
    namespace: str,
    request: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    token: HTTPAuthorizationCredentials = Depends(security),
    credentials: JWTAuthorizer = Depends(authorizer),
    db: Session = Depends(get_db)
):
    
    service = InvenioApplicationPackageService(db, token.credentials)

    jobId = str(uuid.uuid4())

    # Save the uploaded file
    content = await request.read()
    file_path = service.save_uploaded_file(namespace, jobId, content, request.filename)
    
    # Check permissions for namespace...
    # if the namespace is not in the list of groups defined for a user, and it is also NOT the username, they are unauthorized
    # Should be a part of the jwtauth class.
    if not credentials.is_valid_namespace_op(namespace):
        logger.error("User ({}) not in namespace group ({}) or does not match userid.".format(credentials.get_username(), namespace))
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized- you are not allowed to register to this namespace."
        )

    # Validate the package
    is_valid, issues = service.validate_package(file_path)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid application package: " + json.dumps(issues))
    
    # Parse the package
    artifact_name, artifact_version = service.quick_parse(namespace, jobId, request.filename)

    # Create job record
    job = service.create_job(jobId, namespace, request.filename, artifact_name, artifact_version)
    

    # Add background task
    background_tasks.add_task(
        service.process_application_package,
        namespace=namespace,
        filename=request.filename,
        job_id=job.id
    )
    
    return CatalogJobResponse(
        jobId=job.id,
        status="pending",
        message=f"Registration of {request.filename} initiated. Job ID: {job.id}"
    )

@router.get("/{namespace}/{artifactName}", response_model=ApplicationPackageDetails)
async def get_application_package_details(
    namespace: str,
    artifactName: str,
    db: Session = Depends(get_db)

):
    service = ApplicationPackageService(db)
    package = service.get_package(namespace, artifactName)
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    
    return ApplicationPackageDetails.from_db_package_with_versions(package)




@router.get("/{namespace}/{artifactName}/{version}", response_model=ApplicationPackageDetails)
async def get_application_package_details(
    namespace: str,
    artifactName: str,
    version: str,
    token: HTTPAuthorizationCredentials = Depends(security),
    credentials: JWTAuthorizer = Depends(authorizer),
    db: Session = Depends(get_db)
):
    # #service = ApplicationPackageService(db)
    # package = service.get_package(namespace, artifactName)
    
    # if not package:
    #     raise HTTPException(status_code=404, detail="Application package not found")
    
    # return ApplicationPackageDetails.from_rdm_package(package)
    service = InvenioApplicationPackageService(db, token.credentials)
    package = service.get_package(namespace, artifactName)
    
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    
    return package

@router.post("/{namespace}/{artifactName}/{version}/publish", response_model=PublishResponse)
async def publish_application_package(
    namespace: str,
    artifactName: str,
    version: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    service = ApplicationPackageService(db)
    

    try:
        package = service.get_package(namespace, artifactName)
        if not package:
            raise ValueError("Application package not found")

        package_version = service.get_application_package_version(package, version)
        if not package_version:
            raise ValueError("Application package version not found")
        
        package = service.update_package_version_publish_status(package_version, True)
        return PublishResponse(
            namespace=namespace,
            artifactName=artifactName,
            artifactVersion=version,
            published=True,
            message="Package published successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{namespace}/{artifactName}/{version}/unpublish", response_model=PublishResponse)
async def unpublish_application_package(
    namespace: str,
    artifactName: str,
    version: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    service = ApplicationPackageService(db)
    try:
        package = service.update_package_publish_status(namespace, artifactName, version, False)
        return PublishResponse(
            namespace=namespace,
            artifactName=artifactName,
            artifactVersion=version,
            published=False,
            message="Package unpublished successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 