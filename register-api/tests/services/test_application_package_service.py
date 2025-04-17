import os
import cwl_utils
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.application_package_service import ApplicationPackageService
from app.models.application_package_db import ApplicationPackage
from app.models.job import Job, JobStatus
from app.core.config import settings

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def service(mock_db):
    return ApplicationPackageService(mock_db)

@pytest.fixture
def mock_cwl_workflow():
    workflow = MagicMock()
    workflow.id = "test#workflow"
    return workflow

@pytest.fixture
def mock_cwl_tool():
    tool = MagicMock()
    tool.requirements = []
    return tool

def test_validate_package(service):
    with patch('ap_validator.app_package.AppPackage') as mock_app_package:
        mock_app_package.from_url.return_value.check_all.return_value = {'valid': True, 'issues': []}
        is_valid, issues = service.validate_package("tests/data/process_sardem-sarsen_mlucas_nasa-ogc.cwl")
        assert is_valid
        assert issues == []

def test_save_uploaded_file(service):
    with patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        file_path = service.save_uploaded_file("test", b"content", "test.cwl")
        
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_file.write.assert_called_once_with(b"content")
        assert file_path == os.path.join(settings.STORAGE_PATH, "test", "test.cwl")

def test_create_job(service, mock_db):
    job = service.create_job("test", "test.cwl")
    
    assert isinstance(job, Job)
    assert job.status == JobStatus.PENDING
    assert job.namespace == "test"
    assert job.filename == "test.cwl"
    mock_db.add.assert_called_once_with(job)
    mock_db.commit.assert_called_once()

def test_update_job_status(service, mock_db):
    mock_job = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_job
    
    service.update_job_status("job_id", JobStatus.COMPLETED, "Done", 100)
    
    assert mock_job.status == JobStatus.COMPLETED
    assert mock_job.message == "Done"
    assert mock_job.progress == 100
    mock_db.commit.assert_called_once()

def test_parse_cwl_file(service, mock_cwl_workflow, mock_cwl_tool):
    workflow, tool = service.parse_cwl_file("tests/data/process_sardem-sarsen_mlucas_nasa-ogc.cwl")
    
    assert workflow is not None
    assert tool is not None 

def test_extract_docker_image(service):
    workflow, cwltool = service.parse_cwl_file("tests/data/process_sardem-sarsen_mlucas_nasa-ogc.cwl")
    # print(tool)
    print(cwltool.requirements)
    reqs: list[any] = cwltool.requirements
    for req in reqs:
        if "DockerRequirement" in str(type(req)):
            print(req.dockerPull)
    # print(tool.DockerRequirement.dockerPull)

    image = service.extract_docker_image(cwltool)
    assert image == "ghcr.io/maap-project/sardem-sarsen:mlucas_nasa-ogc"

def test_get_or_create_package_new(service, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    package, created = service.get_or_create_package(
        "test", "workflow", "1.0.0", "test/image", "/storage/test/test.cwl", "job_id"
    )
    
    assert created
    assert isinstance(package, ApplicationPackage)
    assert package.namespace == "test"
    assert package.artifact_name == "workflow"
    assert package.artifact_version == "1.0.0"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_get_or_create_package_existing(service, mock_db):
    mock_package = MagicMock(spec=ApplicationPackage)
    mock_package.published = False
    mock_db.query.return_value.filter.return_value.first.return_value = mock_package
    
    package, created = service.get_or_create_package(
        "test", "workflow", "1.0.0", "test/image", "/storage/test/test.cwl", "job_id"
    )
    
    assert created
    assert package == mock_package
    assert package.docker_image == "test/image"
    assert package.cwl_url == "/storage/test/test.cwl"
    assert package.job_id == "job_id"
    mock_db.commit.assert_called_once()

def test_get_or_create_package_published(service, mock_db):
    mock_package = MagicMock(spec=ApplicationPackage)
    mock_package.published = True
    mock_db.query.return_value.filter.return_value.first.return_value = mock_package
    
    package, created = service.get_or_create_package(
        "test", "workflow", "1.0.0", "test/image", "/storage/test/test.cwl", "job_id"
    )
    
    assert not created
    assert package == mock_package

def test_process_application_package_success(service, mock_cwl_workflow, mock_cwl_tool):
    with patch.object(service, 'parse_cwl_file', return_value=(mock_cwl_workflow, mock_cwl_tool)), \
         patch.object(service, 'extract_docker_image', return_value="test/image"), \
         patch.object(service, 'get_or_create_package', return_value=(MagicMock(), True)), \
         patch.object(service, 'update_job_status') as mock_update:
        
        service.process_application_package("test", "test.cwl", "job_id")
        
        assert mock_update.call_count == 2  # Processing, completed

def test_process_application_package_missing_workflow(service, mock_cwl_tool):
    with patch.object(service, 'parse_cwl_file', return_value=(None, mock_cwl_tool)), \
         patch.object(service, 'update_job_status') as mock_update:
        
        service.process_application_package("test", "test.cwl", "job_id")
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "Error processing application package: Invalid CWL file: missing workflow or tool definition"
        )

def test_process_application_package_missing_tool(service, mock_cwl_workflow):
    with patch.object(service, 'parse_cwl_file', return_value=(mock_cwl_workflow, None)), \
         patch.object(service, 'update_job_status') as mock_update:
        
        service.process_application_package("test", "test.cwl", "job_id")
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "Error processing application package: Invalid CWL file: missing workflow or tool definition"
        )

def test_process_application_package_invalid_workflow_id(service, mock_cwl_tool):
    mock_workflow = MagicMock()
    mock_workflow.id = "invalid_id"  # No '#' in ID
    
    with patch.object(service, 'parse_cwl_file', return_value=(mock_workflow, mock_cwl_tool)), \
         patch.object(service, 'update_job_status') as mock_update:
        
        service.process_application_package("test", "test.cwl", "job_id")
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "Error processing application package: Invalid CWL workflow: missing or invalid ID"
        )

def test_process_application_package_package_exists(service, mock_cwl_workflow, mock_cwl_tool):
    mock_package = MagicMock()
    mock_package.namespace = "test"
    mock_package.artifact_name = "workflow"
    mock_package.artifact_version = "1.0.0"
    
    with patch.object(service, 'parse_cwl_file', return_value=(mock_cwl_workflow, mock_cwl_tool)), \
         patch.object(service, 'extract_docker_image', return_value="test/image"), \
         patch.object(service, 'get_or_create_package', return_value=(mock_package, False)), \
         patch.object(service, 'update_job_status') as mock_update:
        
        service.process_application_package("test", "test.cwl", "job_id")
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "A Published Application package with this namespace, name, and version already exists. test/workflow/1.0.0",
            100
        )

def test_extract_artifact_name(service, mock_cwl_workflow):
    assert service._extract_artifact_name(mock_cwl_workflow) == "workflow"

def test_extract_artifact_name_invalid(service):
    mock_workflow = MagicMock()
    mock_workflow.id = "invalid_id"
    
    with pytest.raises(ValueError, match="Invalid CWL workflow: missing or invalid ID"):
        service._extract_artifact_name(mock_workflow)

def test_extract_artifact_version(service, mock_cwl_workflow):
    assert service._extract_artifact_version(mock_cwl_workflow) == "1.0.0"

def test_handle_package_exists(service, mock_db):
    mock_package = MagicMock()
    mock_package.namespace = "test"
    mock_package.artifact_name = "workflow"
    mock_package.artifact_version = "1.0.0"
    
    with patch.object(service, 'update_job_status') as mock_update:
        service._handle_package_exists("job_id", mock_package)
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "A Published Application package with this namespace, name, and version already exists. test/workflow/1.0.0",
            100
        )

def test_handle_successful_processing(service):
    with patch.object(service, 'update_job_status') as mock_update:
        service._handle_successful_processing("job_id")
        
        mock_update.assert_called_with(
            "job_id",
            JobStatus.COMPLETED,
            "Application package processed successfully",
            100
        )

def test_handle_processing_error(service):
    error = Exception("Test error")
    with patch.object(service, 'update_job_status') as mock_update, \
         patch('fastapi.logger.logger.error') as mock_logger:
        
        service._handle_processing_error("job_id", error)
        
        mock_logger.assert_called_once_with("Error processing application package: Test error")
        mock_update.assert_called_with(
            "job_id",
            JobStatus.FAILED,
            "Error processing application package: Test error"
        )

def test_get_package(service, mock_db):
    mock_package = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_package
    
    package = service.get_package("test", "workflow", "1.0.0")
    
    assert package == mock_package

def test_update_package_publish_status(service, mock_db):
    mock_package = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_package
    
    package = service.update_package_publish_status("test", "workflow", "1.0.0", True)
    
    assert package == mock_package
    assert package.published is True
    assert package.published_date is not None
    mock_db.commit.assert_called_once()

def test_update_package_publish_status_not_found(service, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(ValueError, match="Application package not found"):
        service.update_package_publish_status("test", "workflow", "1.0.0", True) 