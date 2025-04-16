from pydantic import BaseModel
from typing import Optional

class CWLUploadRequest(BaseModel):
    cwl: dict
    metadata: Optional[dict] = None 