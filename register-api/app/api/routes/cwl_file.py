from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/{namespace}/{artifactName}/{version}")
async def get_cwl_file(
    namespace: str,
    artifactName: str,
    version: str
):
    # TODO: Implement actual CWL file retrieval logic

    return JSONResponse(
        content={"message": "CWL file content would be here"},
        media_type="application/json"
    ) 