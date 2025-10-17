"""Auto-generated mapper for get_chatsession operation."""

from pydantic_models.base.transformations import BaseMapper
from pydantic_models.operations.chatsession_ops import (
    ChatSessionClosedPayload,
    CloseChatSessionResponse
)
from pydantic_models.canonical.chatsession import ChatSessionModel


class GetChatsessionMapper(BaseMapper[ChatSessionClosedPayload, ChatSessionModel]):
    """Transforms get_chatsession payloads to/from domain models."""

    @classmethod
    def to_domain(cls, payload: ChatSessionClosedPayload) -> ChatSessionModel:
        """Transform request payload to domain model."""
        # TODO: Implement transformation logic
        return ChatSessionModel(
            # Map fields here - customize based on your domain model
            id=cls._generate_id(),
            # Add field mappings...
        )

    @classmethod
    def to_dto(cls, domain: ChatSessionModel) -> CloseChatSessionResponse:
        """Transform domain model to response payload."""
        # TODO: Implement transformation logic
        return CloseChatSessionResponse(
            # Map fields here - customize based on your response model
            # Add field mappings...
        )

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique identifier."""
        import uuid
        return str(uuid.uuid4())
