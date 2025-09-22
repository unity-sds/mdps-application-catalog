from fastapi import APIRouter, Depends, Query

from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.models.package_summary import PackageDiscoveryResponse, ApplicationPackageSummary
from app.models.application_package import ApplicationPackageDetails, ApplicationPackageCreate
from datetime import datetime
from typing import Optional
from app.services.application_package_service import ApplicationPackageService
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/application-packages", response_model=PackageDiscoveryResponse)
async def discover_packages(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    name: Optional[str] = Query(None, description="Filter by application name"),
    published: Optional[bool] = Query(True, description="Filter by publication status"),
    page: int = Query(1, description="Page number for pagination"),
    limit: int = Query(20, description="Number of items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
    ):
    service = ApplicationPackageService(db)

    # TODO: Implement actual package discovery logic and filters
    package_list = service.list_packages(namespace, name)
    plist = []
    for package in package_list:
        p = ApplicationPackageDetails.from_db_package(package)
        plist.append(p)

    return PackageDiscoveryResponse(
        total=1,
        page=page,
        limit=limit,
        packages=plist
    ) 