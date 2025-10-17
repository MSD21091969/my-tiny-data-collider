"""Mapper for create_casefile operation."""

import uuid
from datetime import datetime

from pydantic_models.base.transformations import BaseMapper
from pydantic_models.canonical.casefile import CasefileMetadata, CasefileModel
from pydantic_models.operations.casefile_ops import (
    CreateCasefilePayload,
    CasefileCreatedPayload
)
from pydantic_models.workspace import CasefileGmailData


class CreateCasefileMapper(BaseMapper[CreateCasefilePayload, CasefileModel]):
    """Transforms create_casefile payloads to/from domain models."""

    @classmethod
    def to_domain(cls, payload: CreateCasefilePayload) -> CasefileModel:
        """Transform request payload to domain model."""
        return CasefileModel(
            id=cls._generate_casefile_id(),
            metadata=CasefileMetadata(
                title=payload.title,
                description=payload.description,
                tags=payload.tags,
                created_by="system",  # This would come from request context
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            ),
            # Initialize with empty Gmail data to satisfy validation requirement
            gmail_data=CasefileGmailData()
        )

    @classmethod
    def to_dto(cls, domain: CasefileModel) -> CasefileCreatedPayload:
        """Transform domain model to response payload."""
        return CasefileCreatedPayload(
            casefile_id=domain.id,
            title=domain.metadata.title,
            created_at=domain.metadata.created_at,
            created_by=domain.metadata.created_by
        )

    @staticmethod
    def _generate_casefile_id() -> str:
        """Generate a casefile ID in format cf_yymmdd_xxx."""
        now = datetime.utcnow()
        yy = now.strftime("%y")
        mmdd = now.strftime("%m%d")
        unique_suffix = str(uuid.uuid4())[:3]  # First 3 chars of UUID
        return f"cf_{yy}{mmdd}_{unique_suffix}"
