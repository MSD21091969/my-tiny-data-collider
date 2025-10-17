"""Google Workspace client abstractions used by generated tools."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic_ai_integration.method_decorator import register_service_method
from coreservice.config import get_config
from pydantic_models.workspace import (
    CasefileDriveData,
    CasefileGmailData,
    CasefileSheetsData,
    DriveFile,
    DriveOwner,
    GmailMessage,
    SheetData,
    SheetMetadata,
    SheetRange,
)

from .models import (
    DriveListFilesRequest,
    DriveListFilesResponse,
    GmailGetMessageRequest,
    GmailGetMessageResponse,
    GmailListMessagesRequest,
    GmailListMessagesResponse,
    GmailSearchMessagesRequest,
    GmailSearchMessagesResponse,
    GmailSendMessageRequest,
    GmailSendMessageResponse,
    SheetsBatchGetRequest,
    SheetsBatchGetResponse,
)

logger = logging.getLogger(__name__)


class GmailClient:
    """Gmail client wrapper that can run in mock or real mode."""

    def __init__(self, user_id: str, *, use_mock: Optional[bool] = None) -> None:
        config = get_config()
        self.user_id = user_id
        self._use_mock = config.get("enable_mock_gmail", True) if use_mock is None else use_mock

    @register_service_method(
        name="list_messages",
        description="List Gmail messages",
        service_name="GmailClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "communication",
            "subdomain": "gmail",
            "capability": "read",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:gmail:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def list_messages(
        self,
        request: Optional[GmailListMessagesRequest] = None,
        **kwargs,
    ) -> GmailListMessagesResponse:
        """List Gmail messages for the authenticated user."""

        req = request or GmailListMessagesRequest(**kwargs)

        if self._use_mock:
            logger.debug("Returning mock Gmail messages for user %s", self.user_id)
            now_iso = datetime.now().isoformat()
            mock_messages = [
                GmailMessage(
                    id="mock-msg-1",
                    thread_id="mock-thread-1",
                    subject="Mock subject",
                    sender="notifications@example.com",
                    to_recipients=[f"{self.user_id}@example.com"],
                    snippet="This is a mock Gmail message",
                    internal_date=now_iso,
                    labels=["INBOX", "MOCK"],
                    has_attachments=False,
                    attachments=[],
                    body_text="Mock email body",
                    body_html=None,
                    fetched_at=now_iso,
                ),
                GmailMessage(
                    id="mock-msg-2",
                    thread_id="mock-thread-1",
                    subject="Another mock subject",
                    sender="alerts@example.com",
                    to_recipients=[f"{self.user_id}@example.com"],
                    snippet="Another mock Gmail message",
                    internal_date=now_iso,
                    labels=["INBOX"],
                    has_attachments=True,
                    attachments=[],
                    body_text="Another mock email body",
                    body_html=None,
                    fetched_at=now_iso,
                ),
            ]

            return GmailListMessagesResponse(
                messages=mock_messages,
                result_size_estimate=len(mock_messages),
                next_page_token=None,
            )

        raise NotImplementedError("Real Gmail API integration not yet implemented")

    @register_service_method(
        name="send_message",
        description="Send Gmail message",
        service_name="GmailClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "communication",
            "subdomain": "gmail",
            "capability": "create",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:gmail:write"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def send_message(
        self,
        request: Optional[GmailSendMessageRequest] = None,
        **kwargs,
    ) -> GmailSendMessageResponse:
        """Send a Gmail message."""

        req = request or GmailSendMessageRequest(**kwargs)

        if self._use_mock:
            logger.debug("Sending mock Gmail message from user %s to %s", self.user_id, req.to)
            message_id = f"mock-sent-{datetime.now().timestamp()}"
            thread_id = f"mock-thread-{datetime.now().timestamp()}"
            return GmailSendMessageResponse(
                message_id=message_id,
                thread_id=thread_id,
                label_ids=["SENT"],
            )

        raise NotImplementedError("Real Gmail API integration not yet implemented")

    @register_service_method(
        name="search_messages",
        description="Search Gmail messages by query",
        service_name="GmailClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "communication",
            "subdomain": "gmail",
            "capability": "search",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:gmail:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def search_messages(
        self,
        request: Optional[GmailSearchMessagesRequest] = None,
        **kwargs,
    ) -> GmailSearchMessagesResponse:
        """Search Gmail messages with query."""

        req = request or GmailSearchMessagesRequest(**kwargs)

        if self._use_mock:
            logger.debug("Searching mock Gmail messages for user %s with query: %s", self.user_id, req.query)
            now_iso = datetime.now().isoformat()
            # Mock search results - return messages matching the query keyword
            mock_results = [
                GmailMessage(
                    id="mock-search-1",
                    thread_id="mock-thread-search-1",
                    subject=f"Search Result for: {req.query}",
                    sender="results@example.com",
                    to_recipients=[f"{self.user_id}@example.com"],
                    snippet=f"This message matches your search: {req.query}",
                    internal_date=now_iso,
                    labels=["INBOX", "IMPORTANT"],
                    has_attachments=False,
                    attachments=[],
                    body_text=f"Full body of search result for {req.query}",
                    body_html=None,
                    fetched_at=now_iso,
                ),
            ]

            limited_results = mock_results[: min(req.max_results, len(mock_results))]
            return GmailSearchMessagesResponse(
                messages=limited_results,
                result_size_estimate=len(mock_results),
                next_page_token=None,
                query_used=req.query,
            )

        raise NotImplementedError("Real Gmail API integration not yet implemented")

    @register_service_method(
        name="get_message",
        description="Get single Gmail message by ID",
        service_name="GmailClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "communication",
            "subdomain": "gmail",
            "capability": "read",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:gmail:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def get_message(
        self,
        request: Optional[GmailGetMessageRequest] = None,
        **kwargs,
    ) -> GmailGetMessageResponse:
        """Get a specific Gmail message by ID."""

        req = request or GmailGetMessageRequest(**kwargs)

        if self._use_mock:
            logger.debug("Getting mock Gmail message %s for user %s", req.message_id, self.user_id)
            now_iso = datetime.now().isoformat()
            mock_message = GmailMessage(
                id=req.message_id,
                thread_id=f"mock-thread-{req.message_id}",
                subject="Retrieved Message",
                sender="sender@example.com",
                to_recipients=[f"{self.user_id}@example.com"],
                snippet="This is the message snippet",
                internal_date=now_iso,
                labels=["INBOX"],
                has_attachments=False,
                attachments=[],
                body_text="Full body of the retrieved message",
                body_html=None,
                fetched_at=now_iso,
            )
            return GmailGetMessageResponse(message=mock_message)

        raise NotImplementedError("Real Gmail API integration not yet implemented")

    @staticmethod
    def to_casefile_data(response: GmailListMessagesResponse) -> CasefileGmailData:
        """Convert a Gmail response payload into typed casefile data."""

        gmail_data = CasefileGmailData(
            messages=response.messages,
            synced_at=datetime.now().isoformat(),
            sync_status="completed",
        )
        return gmail_data


class DriveClient:
    """Google Drive client wrapper supporting mock mode."""

    def __init__(self, user_id: str, *, use_mock: Optional[bool] = None) -> None:
        config = get_config()
        self.user_id = user_id
        self._use_mock = config.get("enable_mock_drive", True) if use_mock is None else use_mock

    @register_service_method(
        name="list_files",
        description="List Google Drive files",
        service_name="DriveClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "workspace",
            "subdomain": "google_drive",
            "capability": "read",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:drive:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def list_files(
        self,
        request: Optional[DriveListFilesRequest] = None,
        **kwargs,
    ) -> DriveListFilesResponse:
        """List Drive files for the authenticated user."""

        req = request or DriveListFilesRequest(**kwargs)

        if self._use_mock:
            logger.debug("Returning mock Drive files for user %s", self.user_id)
            now_iso = datetime.now().isoformat()
            mock_files = [
                DriveFile(
                    id="mock-file-1",
                    name="Important Document",
                    mime_type="application/vnd.google-apps.document",
                    owners=[DriveOwner(display_name="Mock Owner", email=f"{self.user_id}@example.com")],
                    parents=["root"],
                    web_view_link="https://drive.google.com/mock-file-1",
                    size_bytes=1024,
                    trashed=False,
                    created_time=now_iso,
                    modified_time=now_iso,
                ),
                DriveFile(
                    id="mock-file-2",
                    name="Quarterly Report",
                    mime_type="application/pdf",
                    owners=[DriveOwner(display_name="Mock Owner", email=f"{self.user_id}@example.com")],
                    parents=["root"],
                    web_view_link="https://drive.google.com/mock-file-2",
                    size_bytes=2048,
                    trashed=False,
                    created_time=now_iso,
                    modified_time=now_iso,
                ),
            ]

            return DriveListFilesResponse(files=mock_files, next_page_token=None)

        raise NotImplementedError("Real Drive API integration not yet implemented")

    async def upload_file(self, file_name: str, content: str = "", mime_type: str = "text/plain") -> dict:
        """Upload a file to Google Drive (mock mode only)."""
        if self._use_mock:
            logger.debug("Mock uploading file %s for user %s", file_name, self.user_id)
            now_iso = datetime.now().isoformat()
            mock_file_id = f"mock-upload-{datetime.now().timestamp()}"
            return {
                "id": mock_file_id,
                "name": file_name,
                "web_view_link": f"https://drive.google.com/{mock_file_id}",
                "created_time": now_iso,
                "size": len(content.encode('utf-8'))
            }
        raise NotImplementedError("Real Drive API integration not yet implemented")

    @staticmethod
    def to_casefile_data(response: DriveListFilesResponse) -> CasefileDriveData:
        """Convert a Drive response payload into typed casefile data."""

        drive_data = CasefileDriveData(
            files=response.files,
            synced_at=datetime.now().isoformat(),
            sync_status="completed",
        )
        return drive_data


class SheetsClient:
    """Google Sheets client wrapper supporting mock mode."""

    def __init__(self, user_id: str, *, use_mock: Optional[bool] = None) -> None:
        config = get_config()
        self.user_id = user_id
        self._use_mock = config.get("enable_mock_sheets", True) if use_mock is None else use_mock

    @register_service_method(
        name="batch_get",
        description="Batch get Google Sheets data",
        service_name="SheetsClient",
        service_module="src.pydantic_ai_integration.integrations.google_workspace.clients",
        classification={
            "domain": "workspace",
            "subdomain": "google_sheets",
            "capability": "read",
            "complexity": "atomic",
            "maturity": "beta",
            "integration_tier": "external"
        },
        required_permissions=["workspace:sheets:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def batch_get(
        self,
        request: Optional[SheetsBatchGetRequest] = None,
        **kwargs,
    ) -> SheetsBatchGetResponse:
        """Retrieve values for multiple ranges within a spreadsheet."""

        req = request or SheetsBatchGetRequest(**kwargs)

        if self._use_mock:
            logger.debug("Returning mock spreadsheet data for user %s", self.user_id)
            now_iso = datetime.now().isoformat()
            sheet_data = SheetData(
                spreadsheet_id=req.spreadsheet_id,
                title="Mock Spreadsheet",
                metadata=[
                    SheetMetadata(
                        sheet_id=1,
                        title="Sheet1",
                        index=0,
                        grid_properties={"rowCount": 100, "columnCount": 26},
                    )
                ],
                ranges=[
                    SheetRange(range=rng, values=[["Mock", "Data"], ["More", "Rows"]])
                    for rng in req.ranges
                ],
                updated_at=now_iso,
            )

            return SheetsBatchGetResponse(spreadsheet=sheet_data)

        raise NotImplementedError("Real Sheets API integration not yet implemented")

    async def create_spreadsheet(self, title: str = "New Spreadsheet") -> dict:
        """Create a new Google Spreadsheet (mock mode only)."""
        if self._use_mock:
            logger.debug("Mock creating spreadsheet '%s' for user %s", title, self.user_id)
            mock_id = f"mock-sheet-{datetime.now().timestamp()}"
            return {
                "spreadsheet_id": mock_id,
                "title": title,
                "sheets": [{"properties": {"sheet_id": 0, "title": "Sheet1"}}],
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{mock_id}"
            }
        raise NotImplementedError("Real Sheets API integration not yet implemented")

    async def update_values(self, spreadsheet_id: str, range_name: str, values: list) -> dict:
        """Update values in a Google Spreadsheet (mock mode only)."""
        if self._use_mock:
            logger.debug("Mock updating range %s in spreadsheet %s for user %s", range_name, spreadsheet_id, self.user_id)
            return {
                "spreadsheet_id": spreadsheet_id,
                "updated_range": range_name,
                "updated_rows": len(values),
                "updated_columns": len(values[0]) if values else 0,
                "updated_cells": sum(len(row) for row in values)
            }
        raise NotImplementedError("Real Sheets API integration not yet implemented")

    @staticmethod
    def to_casefile_data(response: SheetsBatchGetResponse) -> CasefileSheetsData:
        """Convert a Sheets response payload into typed casefile data."""

        sheets_data = CasefileSheetsData(
            spreadsheets={response.spreadsheet.spreadsheet_id: response.spreadsheet},
            synced_at=datetime.now().isoformat(),
            sync_status="completed",
        )
        return sheets_data
