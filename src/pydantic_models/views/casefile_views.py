"""
Casefile view and projection models.

This module contains lightweight projections and summaries of casefile entities:
- CasefileSummary: Lightweight summary for list views

These are used in API responses where full casefile data is not needed.
"""

from pydantic import BaseModel, Field
from typing import List


class CasefileSummary(BaseModel):
    """Summary view of a casefile."""
    casefile_id: str = Field(..., description="Casefile ID in format cf_yymmdd_code")
    title: str = Field(..., description="Casefile title")
    description: str = Field(..., description="Casefile description")
    tags: List[str] = Field(..., description="Casefile tags")
    created_at: str = Field(..., description="Creation timestamp")
    resource_count: int = Field(..., description="Total number of linked resources")
    session_count: int = Field(..., description="Total number of associated sessions")
