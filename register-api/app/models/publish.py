from pydantic import BaseModel
from typing import Optional

class PublishResponse(BaseModel):
    namespace: str
    artifactName: str
    artifactVersion: str
    published: bool
    message: Optional[str] = None 