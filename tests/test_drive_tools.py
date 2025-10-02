"""
Comprehensive test suite for Google Drive tools.

Tests follow pytest patterns from test_example_with_markers.py and fixtures from conftest.py.
These tests validate:
- Parameter validation (Pydantic guardrails)
- Tool execution (business logic)
- Event tracking (audit trail)
- Mock client behavior
- Error handling

Total: 25+ test cases covering all Drive tools.
"""

import pytest
from typing import Dict, Any
from pydantic import ValidationError

from src.pydantic_ai_integration.tools.drive_params import (
    DriveListFilesParams,
    DriveGetFileParams,
    DriveUploadFileParams,
    DriveCreateFolderParams,
    DriveShareFileParams
)
from src.pydantic_ai_integration.tools.drive_tools import (
    drive_list_files,
    drive_get_file,
    drive_upload_file,
    drive_create_folder,
    drive_share_file
)
from src.pydantic_ai_integration.tools.mock_drive_client import (
    MockDriveClient,
    get_mock_drive_client
)
from src.pydantic_ai_integration.dependencies import MDSContext


# ============================================================================
# PARAMETER VALIDATION TESTS (Pydantic Guardrails)
# ============================================================================

@pytest.mark.unit
class TestDriveListFilesParams:
    """Test DriveListFilesParams validation."""
    
    def test_valid_params(self):
        """Test valid parameters are accepted."""
        params = DriveListFilesParams(
            query="type:pdf",
            max_results=25,
            order_by="name"
        )
        assert params.query == "type:pdf"
        assert params.max_results == 25
        assert params.order_by == "name"
    
    def test_default_params(self):
        """Test default parameter values."""
        params = DriveListFilesParams()
        assert params.query == ""
        assert params.max_results == 10
        assert params.order_by == "modifiedTime desc"
    
    def test_query_max_length(self):
        """Test query max length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            DriveListFilesParams(query="x" * 501)
        assert "String should have at most 500 characters" in str(exc_info.value)
    
    def test_max_results_range(self):
        """Test max_results range constraints."""
        # Too low
        with pytest.raises(ValidationError) as exc_info:
            DriveListFilesParams(max_results=0)
        assert "greater than or equal to 1" in str(exc_info.value)
        
        # Too high
        with pytest.raises(ValidationError) as exc_info:
            DriveListFilesParams(max_results=101)
        assert "less than or equal to 100" in str(exc_info.value)
        
        # Valid boundaries
        params1 = DriveListFilesParams(max_results=1)
        assert params1.max_results == 1
        params2 = DriveListFilesParams(max_results=100)
        assert params2.max_results == 100


@pytest.mark.unit
class TestDriveGetFileParams:
    """Test DriveGetFileParams validation."""
    
    def test_valid_params(self):
        """Test valid parameters are accepted."""
        params = DriveGetFileParams(
            file_id="file_abc123",
            include_content=True
        )
        assert params.file_id == "file_abc123"
        assert params.include_content is True
    
    def test_file_id_required(self):
        """Test file_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            DriveGetFileParams()
        assert "Field required" in str(exc_info.value)
    
    def test_file_id_pattern(self):
        """Test file_id format validation."""
        # Invalid characters
        with pytest.raises(ValidationError) as exc_info:
            DriveGetFileParams(file_id="file@123")
        assert "alphanumeric" in str(exc_info.value)
        
        # Valid patterns
        DriveGetFileParams(file_id="abc123")
        DriveGetFileParams(file_id="file_123")
        DriveGetFileParams(file_id="file-abc-123")
    
    def test_include_content_default(self):
        """Test include_content defaults to False."""
        params = DriveGetFileParams(file_id="abc123")
        assert params.include_content is False


@pytest.mark.unit
class TestDriveUploadFileParams:
    """Test DriveUploadFileParams validation."""
    
    def test_valid_params(self):
        """Test valid parameters are accepted."""
        params = DriveUploadFileParams(
            file_name="document.pdf",
            mime_type="application/pdf",
            content="SGVsbG8gV29ybGQh",
            parent_folder_id="folder_123"
        )
        assert params.file_name == "document.pdf"
        assert params.mime_type == "application/pdf"
        assert params.content == "SGVsbG8gV29ybGQh"
        assert params.parent_folder_id == "folder_123"
    
    def test_required_fields(self):
        """Test required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            DriveUploadFileParams()
        errors = str(exc_info.value)
        assert "file_name" in errors
        assert "content" in errors
    
    def test_file_name_length(self):
        """Test file_name length constraints."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            DriveUploadFileParams(file_name="", content="test")
        assert "at least 1 character" in str(exc_info.value)
        
        # Too long
        with pytest.raises(ValidationError) as exc_info:
            DriveUploadFileParams(file_name="x" * 256, content="test")
        assert "at most 255 characters" in str(exc_info.value)
    
    def test_mime_type_default(self):
        """Test mime_type has default value."""
        params = DriveUploadFileParams(file_name="file.bin", content="test")
        assert params.mime_type == "application/octet-stream"
    
    def test_parent_folder_id_pattern(self):
        """Test parent_folder_id format validation."""
        # Invalid characters
        with pytest.raises(ValidationError) as exc_info:
            DriveUploadFileParams(
                file_name="test.txt",
                content="test",
                parent_folder_id="folder@123"
            )
        assert "alphanumeric" in str(exc_info.value)


@pytest.mark.unit
class TestDriveCreateFolderParams:
    """Test DriveCreateFolderParams validation."""
    
    def test_valid_params(self):
        """Test valid parameters are accepted."""
        params = DriveCreateFolderParams(
            folder_name="My Folder",
            parent_folder_id="parent_123"
        )
        assert params.folder_name == "My Folder"
        assert params.parent_folder_id == "parent_123"
    
    def test_folder_name_required(self):
        """Test folder_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            DriveCreateFolderParams()
        assert "Field required" in str(exc_info.value)
    
    def test_folder_name_length(self):
        """Test folder_name length constraints."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            DriveCreateFolderParams(folder_name="")
        assert "at least 1 character" in str(exc_info.value)
        
        # Too long
        with pytest.raises(ValidationError) as exc_info:
            DriveCreateFolderParams(folder_name="x" * 256)
        assert "at most 255 characters" in str(exc_info.value)


@pytest.mark.unit
class TestDriveShareFileParams:
    """Test DriveShareFileParams validation."""
    
    def test_valid_params(self):
        """Test valid parameters are accepted."""
        params = DriveShareFileParams(
            file_id="file_abc123",
            email="user@example.com",
            role="writer",
            generate_link=True
        )
        assert params.file_id == "file_abc123"
        assert params.email == "user@example.com"
        assert params.role == "writer"
        assert params.generate_link is True
    
    def test_file_id_required(self):
        """Test file_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            DriveShareFileParams()
        assert "Field required" in str(exc_info.value)
    
    def test_role_literal(self):
        """Test role must be one of allowed values."""
        # Valid roles
        for role in ["reader", "writer", "commenter", "owner"]:
            params = DriveShareFileParams(file_id="file_123", role=role)
            assert params.role == role
        
        # Invalid role
        with pytest.raises(ValidationError) as exc_info:
            DriveShareFileParams(file_id="file_123", role="admin")
        assert "Input should be" in str(exc_info.value)
    
    def test_email_validation(self):
        """Test email format validation."""
        # Invalid email
        with pytest.raises(ValidationError) as exc_info:
            DriveShareFileParams(file_id="file_123", email="not-an-email")
        assert "Invalid email format" in str(exc_info.value)
        
        # Valid emails
        DriveShareFileParams(file_id="file_123", email="user@example.com")
        DriveShareFileParams(file_id="file_123", email="test.user+tag@domain.co.uk")
    
    def test_defaults(self):
        """Test default values."""
        params = DriveShareFileParams(file_id="file_123")
        assert params.email is None
        assert params.role == "reader"
        assert params.generate_link is False


# ============================================================================
# MOCK CLIENT TESTS
# ============================================================================

@pytest.mark.unit
class TestMockDriveClient:
    """Test MockDriveClient behavior."""
    
    def test_client_initialization(self):
        """Test client initializes with sample files."""
        client = MockDriveClient()
        result = client.list_files()
        assert len(result["files"]) == 3
        # Files are sorted by modifiedTime desc by default
        assert result["files"][0]["name"] == "Budget.xlsx"
    
    def test_list_files_query_filter(self):
        """Test list_files query filtering."""
        client = MockDriveClient()
        
        # Filter by type
        result = client.list_files(query="type:pdf")
        assert len(result["files"]) == 1
        assert result["files"][0]["mime_type"] == "application/pdf"
        
        # Filter by name
        result = client.list_files(query='name contains "report"')
        assert len(result["files"]) == 1
        assert "Report" in result["files"][0]["name"]
    
    def test_list_files_max_results(self):
        """Test list_files respects max_results."""
        client = MockDriveClient()
        result = client.list_files(max_results=2)
        assert len(result["files"]) == 2
    
    def test_list_files_sorting(self):
        """Test list_files sorting."""
        client = MockDriveClient()
        
        # Sort by name ascending
        result = client.list_files(order_by="name")
        names = [f["name"] for f in result["files"]]
        assert names == sorted(names)
        
        # Sort by name descending
        result = client.list_files(order_by="name desc")
        names = [f["name"] for f in result["files"]]
        assert names == sorted(names, reverse=True)
    
    def test_get_file_exists(self):
        """Test get_file with existing file."""
        client = MockDriveClient()
        file_data = client.get_file("file_001")
        assert file_data["id"] == "file_001"
        assert file_data["name"] == "Project Report.pdf"
        assert "content" not in file_data
    
    def test_get_file_with_content(self):
        """Test get_file with content included."""
        client = MockDriveClient()
        file_data = client.get_file("file_001", include_content=True)
        assert "content" in file_data
        assert "Mock" in file_data["content"]
    
    def test_get_file_not_found(self):
        """Test get_file with non-existent file."""
        client = MockDriveClient()
        with pytest.raises(ValueError) as exc_info:
            client.get_file("nonexistent")
        assert "File not found" in str(exc_info.value)
    
    def test_upload_file(self):
        """Test upload_file creates new file."""
        client = MockDriveClient()
        file_data = client.upload_file(
            file_name="test.txt",
            mime_type="text/plain",
            content="Hello World"
        )
        assert file_data["name"] == "test.txt"
        assert file_data["mime_type"] == "text/plain"
        assert file_data["size"] == 11
        assert "id" in file_data
        
        # Verify file can be retrieved
        retrieved = client.get_file(file_data["id"])
        assert retrieved["name"] == "test.txt"
    
    def test_upload_file_with_parent(self):
        """Test upload_file with parent folder."""
        client = MockDriveClient()
        file_data = client.upload_file(
            file_name="test.txt",
            mime_type="text/plain",
            content="Hello",
            parent_folder_id="folder_123"
        )
        assert file_data["parents"] == ["folder_123"]
    
    def test_create_folder(self):
        """Test create_folder creates new folder."""
        client = MockDriveClient()
        folder_data = client.create_folder("My Folder")
        assert folder_data["name"] == "My Folder"
        assert folder_data["mime_type"] == "application/vnd.google-apps.folder"
        assert "id" in folder_data
        
        # Verify folder can be retrieved
        retrieved = client.get_file(folder_data["id"])
        assert retrieved["name"] == "My Folder"
    
    def test_share_file_with_email(self):
        """Test share_file with email."""
        client = MockDriveClient()
        result = client.share_file(
            file_id="file_001",
            email="user@example.com",
            role="writer"
        )
        assert result["permission"]["email_address"] == "user@example.com"
        assert result["permission"]["role"] == "writer"
        assert result["permission"]["type"] == "user"
        assert result["file_id"] == "file_001"
    
    def test_share_file_with_link(self):
        """Test share_file with link generation."""
        client = MockDriveClient()
        result = client.share_file(
            file_id="file_001",
            generate_link=True
        )
        assert "link" in result
        assert "file_001" in result["link"]
    
    def test_share_file_not_found(self):
        """Test share_file with non-existent file."""
        client = MockDriveClient()
        with pytest.raises(ValueError) as exc_info:
            client.share_file("nonexistent")
        assert "File not found" in str(exc_info.value)
    
    def test_singleton_client(self):
        """Test get_mock_drive_client returns singleton."""
        client1 = get_mock_drive_client()
        client2 = get_mock_drive_client()
        assert client1 is client2


# ============================================================================
# TOOL EXECUTION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.mock
class TestDriveListFilesTool:
    """Test drive_list_files tool execution."""
    
    @pytest.mark.asyncio
    async def test_list_files_basic(self, sample_mds_context):
        """Test basic file listing."""
        result = await drive_list_files(
            sample_mds_context,
            query="",
            max_results=10,
            order_by="modifiedTime desc"
        )
        
        assert "files" in result
        assert len(result["files"]) > 0
        assert "total_count" in result
        assert "event_id" in result
        assert result["query"] == ""
    
    @pytest.mark.asyncio
    async def test_list_files_with_query(self, sample_mds_context):
        """Test file listing with query filter."""
        result = await drive_list_files(
            sample_mds_context,
            query="type:pdf"
        )
        
        assert len(result["files"]) == 1
        assert result["files"][0]["mime_type"] == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_list_files_event_tracking(self, sample_mds_context):
        """Test event tracking for list_files."""
        result = await drive_list_files(sample_mds_context)
        
        # Check event was registered
        assert len(sample_mds_context.tool_events) > 0
        last_event = sample_mds_context.tool_events[-1]
        assert last_event.status == "success"
        assert "file_count" in last_event.result_summary


@pytest.mark.integration
@pytest.mark.mock
class TestDriveGetFileTool:
    """Test drive_get_file tool execution."""
    
    @pytest.mark.asyncio
    async def test_get_file_basic(self, sample_mds_context):
        """Test basic file retrieval."""
        result = await drive_get_file(
            sample_mds_context,
            file_id="file_001"
        )
        
        assert "file" in result
        assert result["file"]["id"] == "file_001"
        assert result["file"]["name"] == "Project Report.pdf"
        assert "content" not in result["file"]
    
    @pytest.mark.asyncio
    async def test_get_file_with_content(self, sample_mds_context):
        """Test file retrieval with content."""
        result = await drive_get_file(
            sample_mds_context,
            file_id="file_001",
            include_content=True
        )
        
        assert "file" in result
        assert "content" in result["file"]
        assert "Mock" in result["file"]["content"]
    
    @pytest.mark.asyncio
    async def test_get_file_not_found(self, sample_mds_context):
        """Test error handling for non-existent file."""
        with pytest.raises(ValueError) as exc_info:
            await drive_get_file(
                sample_mds_context,
                file_id="nonexistent"
            )
        assert "File not found" in str(exc_info.value)
        
        # Check error was tracked in event
        last_event = sample_mds_context.tool_events[-1]
        assert last_event.status == "error"


@pytest.mark.integration
@pytest.mark.mock
class TestDriveUploadFileTool:
    """Test drive_upload_file tool execution."""
    
    @pytest.mark.asyncio
    async def test_upload_file_basic(self, sample_mds_context):
        """Test basic file upload."""
        result = await drive_upload_file(
            sample_mds_context,
            file_name="test.txt",
            content="Hello World",
            mime_type="text/plain"
        )
        
        assert "file" in result
        assert result["file"]["name"] == "test.txt"
        assert result["file"]["mime_type"] == "text/plain"
        assert "id" in result["file"]
    
    @pytest.mark.asyncio
    async def test_upload_file_with_parent(self, sample_mds_context):
        """Test file upload with parent folder."""
        result = await drive_upload_file(
            sample_mds_context,
            file_name="test.txt",
            content="Hello",
            parent_folder_id="folder_123"
        )
        
        assert result["file"]["parents"] == ["folder_123"]
    
    @pytest.mark.asyncio
    async def test_upload_file_event_tracking(self, sample_mds_context):
        """Test event tracking for upload."""
        result = await drive_upload_file(
            sample_mds_context,
            file_name="test.txt",
            content="Hello"
        )
        
        last_event = sample_mds_context.tool_events[-1]
        assert last_event.status == "success"
        assert "file_id" in last_event.result_summary


@pytest.mark.integration
@pytest.mark.mock
class TestDriveCreateFolderTool:
    """Test drive_create_folder tool execution."""
    
    @pytest.mark.asyncio
    async def test_create_folder_basic(self, sample_mds_context):
        """Test basic folder creation."""
        result = await drive_create_folder(
            sample_mds_context,
            folder_name="My Folder"
        )
        
        assert "folder" in result
        assert result["folder"]["name"] == "My Folder"
        assert result["folder"]["mime_type"] == "application/vnd.google-apps.folder"
    
    @pytest.mark.asyncio
    async def test_create_folder_with_parent(self, sample_mds_context):
        """Test folder creation with parent."""
        result = await drive_create_folder(
            sample_mds_context,
            folder_name="Subfolder",
            parent_folder_id="parent_123"
        )
        
        assert result["folder"]["parents"] == ["parent_123"]


@pytest.mark.integration
@pytest.mark.mock
class TestDriveShareFileTool:
    """Test drive_share_file tool execution."""
    
    @pytest.mark.asyncio
    async def test_share_file_with_email(self, sample_mds_context):
        """Test sharing file with email."""
        result = await drive_share_file(
            sample_mds_context,
            file_id="file_001",
            email="user@example.com",
            role="writer"
        )
        
        assert "permission" in result
        assert result["permission"]["email_address"] == "user@example.com"
        assert result["permission"]["role"] == "writer"
    
    @pytest.mark.asyncio
    async def test_share_file_with_link(self, sample_mds_context):
        """Test sharing file with link generation."""
        result = await drive_share_file(
            sample_mds_context,
            file_id="file_001",
            generate_link=True
        )
        
        assert "link" in result
        assert "file_001" in result["link"]
    
    @pytest.mark.asyncio
    async def test_share_file_not_found(self, sample_mds_context):
        """Test error handling for non-existent file."""
        with pytest.raises(ValueError) as exc_info:
            await drive_share_file(
                sample_mds_context,
                file_id="nonexistent"
            )
        assert "File not found" in str(exc_info.value)


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_query(self):
        """Test empty query is accepted."""
        params = DriveListFilesParams(query="")
        assert params.query == ""
    
    def test_max_query_length(self):
        """Test query at maximum length."""
        params = DriveListFilesParams(query="x" * 500)
        assert len(params.query) == 500
    
    def test_min_max_results(self):
        """Test max_results boundary values."""
        params1 = DriveListFilesParams(max_results=1)
        assert params1.max_results == 1
        
        params2 = DriveListFilesParams(max_results=100)
        assert params2.max_results == 100
    
    def test_optional_parent_folder(self):
        """Test parent_folder_id can be None."""
        params = DriveUploadFileParams(
            file_name="test.txt",
            content="test",
            parent_folder_id=None
        )
        assert params.parent_folder_id is None
    
    def test_optional_email(self):
        """Test email can be None."""
        params = DriveShareFileParams(
            file_id="file_123",
            email=None
        )
        assert params.email is None
