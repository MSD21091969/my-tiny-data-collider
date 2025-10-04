"""
View and projection models.

This package contains lightweight summaries and projections of canonical entities:
- casefile_views.py: CasefileSummary
- session_views.py: SessionSummary, ChatSessionSummary

These are used in API responses where full entity data is not needed.
"""

from .casefile_views import CasefileSummary
from .session_views import SessionSummary, ChatSessionSummary

__all__ = [
    "CasefileSummary",
    "SessionSummary",
    "ChatSessionSummary",
]
