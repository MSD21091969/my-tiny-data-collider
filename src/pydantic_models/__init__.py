"""
Pydantic models package - Domain models organized by purpose.

Directory Structure:
- base/: Infrastructure models (BaseRequest, BaseResponse, RequestEnvelope)
- canonical/: Domain entities (CasefileModel, ToolSession, ChatSession, ACL)
- workspace/: External workspace data (Gmail, Drive, Sheets)
- operations/: Request/response models for service operations
- views/: Summary and projection models

For integration and tool models, see:
- src/pydantic_ai_integration/integrations/ (LAYER 2: External API contracts)
- src/pydantic_ai_integration/tools/generated/ (LAYER 3: Generated tool params)
"""

__version__ = "0.1.0"

# Export base infrastructure for convenience
from .base import BaseRequest, BaseResponse, RequestEnvelope, RequestStatus

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "RequestEnvelope",
    "RequestStatus",
]
