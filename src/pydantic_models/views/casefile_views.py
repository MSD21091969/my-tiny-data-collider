"""
Casefile view and projection models.

This module contains lightweight projections and summaries of casefile entities:
- CasefileSummary: Lightweight summary for list views

These are used in API responses where full casefile data is not needed.
"""

from typing import List

from pydantic import BaseModel, Field

from ..base.custom_types import CasefileId, IsoTimestamp, MediumString, NonNegativeInt, ShortString, TagList


class CasefileSummary(BaseModel):
    """Summary view of a casefile."""
    casefile_id: CasefileId = Field(..., description="Casefile ID in format cf_yymmdd_code")
    title: ShortString = Field(..., description="Casefile title")
    description: MediumString = Field(..., description="Casefile description")
    tags: TagList = Field(..., description="Casefile tags")
    created_at: IsoTimestamp = Field(..., description="Creation timestamp")
    resource_count: NonNegativeInt = Field(..., description="Total number of linked resources")
    session_count: NonNegativeInt = Field(..., description="Total number of associated sessions")
