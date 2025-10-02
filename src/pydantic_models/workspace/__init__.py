"""Typed workspace data models for casefile storage and tool outputs."""

from .gmail import (
    GmailAttachment,
    GmailLabel,
    GmailMessage,
    GmailThread,
    CasefileGmailData,
)
from .drive import (
    DriveOwner,
    DriveFile,
    DriveFolder,
    CasefileDriveData,
)
from .sheets import (
    SheetRange,
    SheetMetadata,
    SheetData,
    CasefileSheetsData,
)

__all__ = [
    "GmailAttachment",
    "GmailLabel",
    "GmailMessage",
    "GmailThread",
    "CasefileGmailData",
    "DriveOwner",
    "DriveFile",
    "DriveFolder",
    "CasefileDriveData",
    "SheetRange",
    "SheetMetadata",
    "SheetData",
    "CasefileSheetsData",
]
