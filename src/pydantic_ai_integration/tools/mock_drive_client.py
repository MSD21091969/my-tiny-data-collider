"""
Mock Google Drive API client for testing.

This client simulates Google Drive API responses without requiring real credentials.
Used for Week 2 mock tool implementation following the Tool Engineering Foundation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import string


class MockDriveClient:
    """
    Mock Google Drive API client that simulates Drive operations.
    
    Returns realistic mock data for testing tool implementations.
    In Week 4, this will be replaced with real Google Drive API calls.
    """
    
    def __init__(self):
        """Initialize mock client with in-memory storage."""
        self._files: Dict[str, Dict[str, Any]] = {}
        self._permissions: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_sample_files()
    
    def _initialize_sample_files(self):
        """Create some sample files for consistent testing."""
        sample_files = [
            {
                "id": "file_001",
                "name": "Project Report.pdf",
                "mime_type": "application/pdf",
                "created_time": "2025-01-15T10:30:00Z",
                "modified_time": "2025-01-20T15:45:00Z",
                "size": 245760,
                "parents": ["root"]
            },
            {
                "id": "file_002",
                "name": "Meeting Notes.docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "created_time": "2025-01-18T09:00:00Z",
                "modified_time": "2025-01-18T11:30:00Z",
                "size": 15360,
                "parents": ["root"]
            },
            {
                "id": "file_003",
                "name": "Budget.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "created_time": "2025-01-10T14:20:00Z",
                "modified_time": "2025-01-22T16:00:00Z",
                "size": 51200,
                "parents": ["root"]
            }
        ]
        
        for file_data in sample_files:
            self._files[file_data["id"]] = file_data
    
    def _generate_file_id(self) -> str:
        """Generate a random file ID."""
        return "file_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    def list_files(
        self,
        query: str = "",
        max_results: int = 10,
        order_by: str = "modifiedTime desc"
    ) -> Dict[str, Any]:
        """
        List files from mock Drive storage.
        
        Args:
            query: Search query (simplified mock implementation)
            max_results: Maximum number of files to return
            order_by: Sort order
            
        Returns:
            Dictionary with files list and metadata
        """
        files = list(self._files.values())
        
        # Simple query filtering (mock implementation)
        if query:
            if "type:pdf" in query:
                files = [f for f in files if f["mime_type"] == "application/pdf"]
            elif "name contains" in query:
                # Extract search term from query
                import re
                match = re.search(r'name contains ["\']([^"\']+)["\']', query)
                if match:
                    search_term = match.group(1).lower()
                    files = [f for f in files if search_term in f["name"].lower()]
        
        # Sort files
        if "name" in order_by:
            files.sort(key=lambda f: f["name"], reverse="desc" in order_by)
        elif "createdTime" in order_by:
            files.sort(key=lambda f: f["created_time"], reverse="desc" in order_by)
        else:  # Default to modifiedTime
            files.sort(key=lambda f: f["modified_time"], reverse="desc" in order_by)
        
        # Limit results
        files = files[:max_results]
        
        return {
            "files": files,
            "next_page_token": None,
            "total_count": len(files)
        }
    
    def get_file(
        self,
        file_id: str,
        include_content: bool = False
    ) -> Dict[str, Any]:
        """
        Get file metadata (and optionally content) from mock storage.
        
        Args:
            file_id: File identifier
            include_content: Whether to include file content
            
        Returns:
            Dictionary with file metadata and optional content
            
        Raises:
            ValueError: If file not found
        """
        if file_id not in self._files:
            raise ValueError(f"File not found: {file_id}")
        
        file_data = self._files[file_id].copy()
        
        if include_content:
            # Mock content based on file type
            if file_data["mime_type"] == "application/pdf":
                file_data["content"] = "Mock PDF content for " + file_data["name"]
            elif "document" in file_data["mime_type"]:
                file_data["content"] = "Mock document content for " + file_data["name"]
            elif "spreadsheet" in file_data["mime_type"]:
                file_data["content"] = "Mock spreadsheet content for " + file_data["name"]
            else:
                file_data["content"] = "Mock content for " + file_data["name"]
        
        return file_data
    
    def upload_file(
        self,
        file_name: str,
        mime_type: str,
        content: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to mock Drive storage.
        
        Args:
            file_name: Name for the file
            mime_type: MIME type
            content: File content
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Dictionary with uploaded file metadata
        """
        file_id = self._generate_file_id()
        now = datetime.now().isoformat() + "Z"
        
        file_data = {
            "id": file_id,
            "name": file_name,
            "mime_type": mime_type,
            "created_time": now,
            "modified_time": now,
            "size": len(content),
            "parents": [parent_folder_id if parent_folder_id else "root"]
        }
        
        self._files[file_id] = file_data
        
        return file_data
    
    def create_folder(
        self,
        folder_name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a folder in mock Drive storage.
        
        Args:
            folder_name: Name for the folder
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Dictionary with created folder metadata
        """
        folder_id = self._generate_file_id()
        now = datetime.now().isoformat() + "Z"
        
        folder_data = {
            "id": folder_id,
            "name": folder_name,
            "mime_type": "application/vnd.google-apps.folder",
            "created_time": now,
            "modified_time": now,
            "size": 0,
            "parents": [parent_folder_id if parent_folder_id else "root"]
        }
        
        self._files[folder_id] = folder_data
        
        return folder_data
    
    def share_file(
        self,
        file_id: str,
        email: Optional[str] = None,
        role: str = "reader",
        generate_link: bool = False
    ) -> Dict[str, Any]:
        """
        Share a file (add permissions) in mock Drive storage.
        
        Args:
            file_id: File to share
            email: Optional email address
            role: Permission role
            generate_link: Whether to generate shareable link
            
        Returns:
            Dictionary with permission info and optional link
            
        Raises:
            ValueError: If file not found
        """
        if file_id not in self._files:
            raise ValueError(f"File not found: {file_id}")
        
        permission_id = "perm_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
        
        permission_data = {
            "id": permission_id,
            "type": "user" if email else "anyone",
            "role": role,
            "email_address": email
        }
        
        # Store permission
        if file_id not in self._permissions:
            self._permissions[file_id] = []
        self._permissions[file_id].append(permission_data)
        
        result = {
            "permission": permission_data,
            "file_id": file_id
        }
        
        if generate_link:
            result["link"] = f"https://drive.google.com/file/d/{file_id}/view"
        
        return result


# Singleton instance for testing
_mock_client = None

def get_mock_drive_client() -> MockDriveClient:
    """Get singleton instance of mock Drive client."""
    global _mock_client
    if _mock_client is None:
        _mock_client = MockDriveClient()
    return _mock_client
