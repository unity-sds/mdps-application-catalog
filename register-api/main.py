from fastapi import FastAPI
from app.api.routes import (
    catalog_job,
    application_package,
    cwl_file,
    discovery
)
from app.core.security import security

app = FastAPI(
    title="Artifact Catalog API",
    description="API for the NASA Artifact Catalog system that manages OGC application packages (CWL files + Docker containers).",
    version="1.0.0"
)

# Include routers
app.include_router(catalog_job.router, prefix="/catalog-job")
app.include_router(application_package.router)
app.include_router(cwl_file.router, prefix="/cwl")
app.include_router(discovery.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 