from fastapi import APIRouter, Depends, Query

from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.models.package_summary import PackageDiscoveryResponse, ApplicationPackageSummary
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/application-packages", response_model=PackageDiscoveryResponse)
async def discover_packages(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    name: Optional[str] = Query(None, description="Filter by application name"),
    published: Optional[bool] = Query(True, description="Filter by publication status"),
    page: int = Query(1, description="Page number for pagination"),
    limit: int = Query(20, description="Number of items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # TODO: Implement actual package discovery logic
    sample_package = ApplicationPackageSummary(
        namespace="sample",
        artifactName="sample-app",
        artifactVersion="1.0.0",
        dateCreated=datetime.now(),
        published=True
    )
    
    return PackageDiscoveryResponse(
        total=1,
        page=page,
        limit=limit,
        packages=[sample_package]
    ) 