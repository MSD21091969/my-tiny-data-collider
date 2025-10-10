"""Typed workspace data models for casefile storage and tool outputs."""

from .drive import (
    CasefileDriveData,
    DriveFile,
    DriveFolder,
    DriveOwner,
)
from .gmail import (
    CasefileGmailData,
    GmailAttachment,
    GmailLabel,
    GmailMessage,
    GmailThread,
)
from .sheets import (
    CasefileSheetsData,
    SheetData,
    SheetMetadata,
    SheetRange,
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
