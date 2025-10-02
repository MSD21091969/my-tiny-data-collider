"""Google Workspace client abstractions used by generated tools."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from ...coreservice.config import get_config
from ...pydantic_models.workspace import (
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
    GmailListMessagesRequest,
    GmailListMessagesResponse,
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

    @staticmethod
    def to_casefile_data(response: SheetsBatchGetResponse) -> CasefileSheetsData:
        """Convert a Sheets response payload into typed casefile data."""

        sheets_data = CasefileSheetsData(
            spreadsheets={response.spreadsheet.spreadsheet_id: response.spreadsheet},
            synced_at=datetime.now().isoformat(),
            sync_status="completed",
        )
        return sheets_data
