
from sqlalchemy.orm import Session
from app.services.invenio_application_package_service import ApplicationPackageService as InvenioService
from app.services.application_package_service import ApplicationPackageService as DBService
from app.core.config import settings

def get_application_pacakge_service(db: Session, token: str):
    if settings.RDM_URL is None:
        print("Returning DBService")
        return DBService(db=db)
    else:
        print("Returning RDMService")
        return InvenioService(db=db, token=token)