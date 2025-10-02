"""
Parameter models for Google Drive tools.

Following the Tool Engineering Foundation pattern from unified_example_tools.py,
these Pydantic models define:
- WHAT parameters each tool accepts (field names and types)
- WHAT constraints apply (ge=, le=, min_length=, etc.) - the GUARDRAILS
- WHAT documentation to show (Field descriptions)

These models serve as:
1. Validation schemas (Pydantic enforces at runtime)
2. Type hints (MyPy/Pylance check at compile time)
3. OpenAPI documentation (FastAPI generates Swagger UI forms)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import re


class DriveListFilesParams(BaseModel):
    """
    Parameters for drive_list_files tool.
    
    METADATA:
    - Tool: drive_list_files
    - Purpose: List files from Google Drive with filtering
    
    GUARDRAILS:
    - query: Max 500 chars (prevent abuse)
    - max_results: Between 1-100 (reasonable range)
    - order_by: Common sort patterns
    """
    query: str = Field(
        "",
        max_length=500,
        description="Google Drive search query (e.g., 'type:pdf', 'name contains \"report\"')",
        examples=["type:pdf", "name contains 'report'", "modifiedTime > '2025-01-01'"]
    )
    max_results: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of files to return",
        examples=[10, 25, 50]
    )
    order_by: str = Field(
        "modifiedTime desc",
        description="Sort order (e.g., 'modifiedTime desc', 'name', 'createdTime')",
        examples=["modifiedTime desc", "name", "createdTime desc"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "type:pdf",
                "max_results": 10,
                "order_by": "modifiedTime desc"
            }
        }


class DriveGetFileParams(BaseModel):
    """
    Parameters for drive_get_file tool.
    
    METADATA:
    - Tool: drive_get_file
    - Purpose: Get metadata and content of a specific file
    
    GUARDRAILS:
    - file_id: Min 1 char, max 200 chars, alphanumeric + dash/underscore only
    - include_content: Boolean flag for content inclusion
    """
    file_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Google Drive file ID",
        examples=["1abc-xyz_123", "abc123def456"]
    )
    include_content: bool = Field(
        False,
        description="Whether to include file content in response",
        examples=[False, True]
    )
    
    @field_validator('file_id')
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """Validate file_id format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("file_id must contain only alphanumeric characters, dashes, and underscores")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "1abc-xyz_123",
                "include_content": False
            }
        }


class DriveUploadFileParams(BaseModel):
    """
    Parameters for drive_upload_file tool.
    
    METADATA:
    - Tool: drive_upload_file
    - Purpose: Upload a file to Google Drive
    
    GUARDRAILS:
    - file_name: Min 1 char, max 255 chars (file system limits)
    - mime_type: Valid MIME type string
    - parent_folder_id: Optional, alphanumeric format
    - content: Required, file content (base64 for binary)
    """
    file_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name for the uploaded file",
        examples=["document.pdf", "report.docx", "data.csv"]
    )
    mime_type: str = Field(
        "application/octet-stream",
        description="MIME type of the file",
        examples=["application/pdf", "text/plain", "application/vnd.google-apps.document"]
    )
    parent_folder_id: Optional[str] = Field(
        None,
        description="Parent folder ID (optional, defaults to root)",
        examples=["1abc-xyz_123", None]
    )
    content: str = Field(
        ...,
        description="File content (base64 encoded for binary files)",
        examples=["SGVsbG8gV29ybGQh"]  # "Hello World!" in base64
    )
    
    @field_validator('parent_folder_id')
    @classmethod
    def validate_parent_folder_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate parent_folder_id format if provided."""
        if v is not None and v != "" and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("parent_folder_id must contain only alphanumeric characters, dashes, and underscores")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "document.pdf",
                "mime_type": "application/pdf",
                "parent_folder_id": None,
                "content": "SGVsbG8gV29ybGQh"
            }
        }


class DriveCreateFolderParams(BaseModel):
    """
    Parameters for drive_create_folder tool.
    
    METADATA:
    - Tool: drive_create_folder
    - Purpose: Create a new folder in Google Drive
    
    GUARDRAILS:
    - folder_name: Min 1 char, max 255 chars
    - parent_folder_id: Optional, alphanumeric format
    """
    folder_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name for the new folder",
        examples=["Project Files", "Reports 2025", "Archive"]
    )
    parent_folder_id: Optional[str] = Field(
        None,
        description="Parent folder ID (optional, defaults to root)",
        examples=["1abc-xyz_123", None]
    )
    
    @field_validator('parent_folder_id')
    @classmethod
    def validate_parent_folder_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate parent_folder_id format if provided."""
        if v is not None and v != "" and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("parent_folder_id must contain only alphanumeric characters, dashes, and underscores")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "folder_name": "Project Files",
                "parent_folder_id": None
            }
        }


class DriveShareFileParams(BaseModel):
    """
    Parameters for drive_share_file tool.
    
    METADATA:
    - Tool: drive_share_file
    - Purpose: Share a file with users or generate shareable link
    
    GUARDRAILS:
    - file_id: Min 1 char, alphanumeric format
    - email: Optional, valid email format
    - role: One of: reader, writer, commenter, owner
    - generate_link: Boolean flag
    """
    file_id: str = Field(
        ...,
        min_length=1,
        description="Google Drive file ID to share",
        examples=["1abc-xyz_123", "abc123def456"]
    )
    email: Optional[str] = Field(
        None,
        description="Email address to share with (optional)",
        examples=["user@example.com", None]
    )
    role: Literal["reader", "writer", "commenter", "owner"] = Field(
        "reader",
        description="Permission role to grant",
        examples=["reader", "writer", "commenter"]
    )
    generate_link: bool = Field(
        False,
        description="Whether to generate a shareable link",
        examples=[False, True]
    )
    
    @field_validator('file_id')
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """Validate file_id format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("file_id must contain only alphanumeric characters, dashes, and underscores")
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format if provided."""
        if v is not None and v != "":
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError("Invalid email format")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "1abc-xyz_123",
                "email": "user@example.com",
                "role": "reader",
                "generate_link": False
            }
        }


# NOTES ON ADDING NEW DRIVE TOOL PARAMETERS:
#
# 1. Create a new class inheriting from BaseModel
# 2. Name it Drive<ToolName>Params (convention)
# 3. Add Field() for each parameter with:
#    - Type annotation (int, str, bool, Optional[], Literal[], etc.)
#    - ... or default value
#    - Constraints (ge=, le=, min_length=, pattern=, etc.) <- GUARDRAILS
#    - description= for API docs <- METADATA
#    - examples= for Swagger UI <- METADATA
# 4. Add @field_validator for complex validation if needed
# 5. Add Config with json_schema_extra example <- METADATA
#
# Follow the patterns established in unified_example_tools.py and tool_params.py
