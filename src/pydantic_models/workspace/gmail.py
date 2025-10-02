"""Pydantic models for Gmail data stored in casefiles and used by tools."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class GmailAttachment(BaseModel):
    """Metadata describing a Gmail attachment."""

    filename: str = Field(..., description="Attachment filename")
    mime_type: str = Field(..., description="Attachment MIME type")
    size_bytes: int = Field(..., ge=0, description="Attachment size in bytes")
    attachment_id: str = Field(..., description="Gmail attachment identifier")


class GmailMessage(BaseModel):
    """Envelope + payload for a Gmail message."""

    id: str = Field(..., description="Gmail message ID")
    thread_id: str = Field(..., description="Thread ID for the message")
    subject: str = Field("", description="Message subject")
    sender: str = Field(..., description="From email address")
    to_recipients: List[str] = Field(default_factory=list, description="Primary recipient email addresses")
    cc_recipients: List[str] = Field(default_factory=list, description="CC recipient email addresses")
    bcc_recipients: List[str] = Field(default_factory=list, description="BCC recipient email addresses")
    snippet: str = Field("", description="Short snippet preview from Gmail")
    internal_date: str = Field(..., description="Gmail internal timestamp (ISO 8601)")
    labels: List[str] = Field(default_factory=list, description="Gmail labels applied to the message")
    has_attachments: bool = Field(default=False, description="Whether the message has attachments")
    attachments: List[GmailAttachment] = Field(default_factory=list, description="Attachment metadata")
    body_text: Optional[str] = Field(None, description="Plaintext body, if available")
    body_html: Optional[str] = Field(None, description="HTML body, if available")
    fetched_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp when data was fetched")


class GmailThread(BaseModel):
    """Thread metadata for a set of Gmail messages."""

    id: str = Field(..., description="Gmail thread ID")
    message_ids: List[str] = Field(default_factory=list, description="Ordered list of message IDs in this thread")
    snippet: str = Field("", description="Thread snippet")
    history_id: Optional[str] = Field(None, description="Gmail history ID for incremental sync")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last time the thread was updated")


class GmailLabel(BaseModel):
    """Representation of a Gmail label."""

    id: str = Field(..., description="Label identifier")
    name: str = Field(..., description="Label name")
    label_type: str = Field(default="user", description="Label type (system or user)")
    message_visibility: str = Field(default="show", description="Whether messages with the label are shown in list views")


class CasefileGmailData(BaseModel):
    """Typed Gmail data stored on a casefile."""

    messages: List[GmailMessage] = Field(default_factory=list, description="Messages stored on the casefile")
    threads: List[GmailThread] = Field(default_factory=list, description="Thread metadata")
    labels: List[GmailLabel] = Field(default_factory=list, description="Cached Gmail labels")
    last_sync_token: Optional[str] = Field(None, description="Token for incremental sync operations")
    synced_at: Optional[str] = Field(None, description="Timestamp of the most recent successful sync")
    sync_status: str = Field(default="idle", description="Current sync status (idle|syncing|error)")
    error_message: Optional[str] = Field(None, description="Last sync error message, if any")

    @computed_field
    def unread_count(self) -> int:
        """Total unread messages across the cached dataset."""

        return sum(1 for message in self.messages if "UNREAD" in message.labels)

    def upsert_messages(self, new_messages: List[GmailMessage]) -> None:
        """Merge new messages into the casefile cache, updating by message ID."""

        index = {message.id: message for message in self.messages}
        for message in new_messages:
            index[message.id] = message
        self.messages = list(index.values())

    def upsert_threads(self, new_threads: List[GmailThread]) -> None:
        """Merge thread metadata into the cache."""

        index = {thread.id: thread for thread in self.threads}
        for thread in new_threads:
            index[thread.id] = thread
        self.threads = list(index.values())

    def upsert_labels(self, new_labels: List[GmailLabel]) -> None:
        """Merge labels into the cache."""

        index = {label.id: label for label in self.labels}
        for label in new_labels:
            index[label.id] = label
        self.labels = list(index.values())
