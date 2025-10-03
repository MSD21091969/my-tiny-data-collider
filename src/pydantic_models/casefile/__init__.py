"""
Initialization file for casefile models.
"""

from .models import (
    CasefileMetadata,
    CasefileModel,
    CasefileSummary,
    ResourceReference,
)

from .crud_models import (
    # Create Casefile
    CreateCasefilePayload,
    CreateCasefileRequest,
    CasefileCreatedPayload,
    CreateCasefileResponse,
    # Get Casefile
    GetCasefilePayload,
    GetCasefileRequest,
    CasefileDataPayload,
    GetCasefileResponse,
    # Update Casefile
    UpdateCasefilePayload,
    UpdateCasefileRequest,
    CasefileUpdatedPayload,
    UpdateCasefileResponse,
    # List Casefiles
    ListCasefilesPayload,
    ListCasefilesRequest,
    CasefileListPayload,
    ListCasefilesResponse,
    # Delete Casefile
    DeleteCasefilePayload,
    DeleteCasefileRequest,
    CasefileDeletedPayload,
    DeleteCasefileResponse,
    # Add Session to Casefile
    AddSessionToCasefilePayload,
    AddSessionToCasefileRequest,
    SessionAddedPayload,
    AddSessionToCasefileResponse,
)

__all__ = [
    # Original models
    "CasefileMetadata",
    "CasefileModel",
    "CasefileSummary",
    "ResourceReference",
    # CRUD operation models
    "CreateCasefilePayload",
    "CreateCasefileRequest",
    "CasefileCreatedPayload",
    "CreateCasefileResponse",
    "GetCasefilePayload",
    "GetCasefileRequest",
    "CasefileDataPayload",
    "GetCasefileResponse",
    "UpdateCasefilePayload",
    "UpdateCasefileRequest",
    "CasefileUpdatedPayload",
    "UpdateCasefileResponse",
    "ListCasefilesPayload",
    "ListCasefilesRequest",
    "CasefileListPayload",
    "ListCasefilesResponse",
    "DeleteCasefilePayload",
    "DeleteCasefileRequest",
    "CasefileDeletedPayload",
    "DeleteCasefileResponse",
    "AddSessionToCasefilePayload",
    "AddSessionToCasefileRequest",
    "SessionAddedPayload",
    "AddSessionToCasefileResponse",
]