from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.services.application_package_service import ApplicationPackageService

router = APIRouter()

@router.get("/{namespace}/{artifactName}/{version}")
async def get_cwl_file(
    namespace: str,
    artifactName: str,
    version: str,
    db: Session = Depends(get_db)
):
    service = ApplicationPackageService(db)
    filepath = service.get_cwl_file_path(namespace, artifactName, version)
    
    return FileResponse(filepath)