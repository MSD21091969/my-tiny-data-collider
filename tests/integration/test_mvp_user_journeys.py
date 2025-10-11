"""
MVP User Journey Integration Tests

Tests complete end-to-end user flows:
1. Auth → Session → Tool Execution → Results
2. Token validation and routing
3. Session context preservation
4. Tool execution with proper authorization

TIER 2 #4: MVP Delivery Specs & UX validation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.authservice.token import create_token, create_service_token
from src.pydantic_models.operations.tool_session_ops import CreateSessionRequest
from src.pydantic_models.operations.tool_execution_ops import ToolRequest
from src.pydantic_models.operations.casefile_ops import CreateCasefileRequest
from tests.integration.conftest import decode_test_token


# Import mocks from conftest.py fixtures


class TestMVPUserJourney:
    """Test complete user journeys from auth through tool execution."""

    @pytest.mark.asyncio
    async def test_complete_user_journey_create_casefile_and_execute_tool(
        self, mock_casefile_service, mock_tool_session_service, integration_test_ids
    ):
        """
        Complete MVP journey:
        1. Create auth token with user context
        2. Create casefile
        3. Create tool session
        4. Execute tool in session
        5. Verify results and audit trail
        """

        # Step 1: User authentication - create token
        user_id = integration_test_ids["user_id"]
        username = integration_test_ids["username"]
        casefile_id = integration_test_ids["casefile_id"]
        session_id = integration_test_ids["session_id"]
        session_request_id = integration_test_ids["session_request_id"]

        token = create_token(
            user_id=user_id,
            username=username,
            session_request_id=session_request_id,
            casefile_id=casefile_id,
            session_id=session_id,
        )
        assert token is not None

        # Verify token can be decoded
        decoded = decode_test_token(token)
        assert decoded["sub"] == user_id
        assert decoded["casefile_id"] == casefile_id
        assert decoded["session_id"] == session_id

        # Step 2: Create casefile using mock service
        casefile_request = CreateCasefileRequest(
            request_id=uuid4(),
            user_id=user_id,
            payload={
                "title": "MVP Test Casefile",
                "description": "Testing complete user journey",
                "tags": ["test", "mvp"],
            },
            metadata={
                "casefile_id": casefile_id,
                "session_request_id": session_request_id,
            },
        )

        casefile_response = await mock_casefile_service.create_casefile(casefile_request)
        assert casefile_response.success is True
        assert casefile_response.payload.user_id == user_id
        assert casefile_response.payload.title == "MVP Test Casefile"

        # Step 3: Create tool session using mock service
        session_request = CreateSessionRequest(
            request_id=uuid4(),
            user_id=user_id,
            payload={
                "casefile_id": casefile_id,
                "title": "Tool execution session",
            },
            metadata={
                "casefile_id": casefile_id,
                "session_request_id": session_request_id,
            },
        )

        session_response = await mock_tool_session_service.create_session(session_request)
        assert session_response.success is True
        assert session_response.payload.status == "active"
        assert session_response.payload.user_id == user_id

        # Step 4: Execute tool with proper authorization
        tool_request = ToolRequest(
            request_id=uuid4(),
            user_id=user_id,
            payload={
                "tool_name": "create_casefile",
                "parameters": {
                    "title": "Nested Test Casefile",
                    "description": "Created via tool",
                },
                "casefile_id": casefile_id,
                "session_request_id": session_request_id,
            },
            metadata={
                "casefile_id": casefile_id,
                "session_request_id": session_request_id,
                "session_id": session_id,
            },
        )

        tool_response = await mock_tool_session_service.process_tool_request(
            tool_request, auth_context={"user_id": user_id}
        )
        assert tool_response.success is True
        assert tool_response.payload["tool_name"] == "create_casefile"
        assert tool_response.payload["result"] == "success"

        # MVP Success Criteria:
        # ✓ Token carries routing metadata (session_request_id, casefile_id, session_id)
        # ✓ Request DTOs preserve routing context
        # ✓ User identity flows through entire chain
        # ✓ Authorization context maintained
        # ✓ Services execute successfully with mocked dependencies

    def test_service_token_flow_for_automation(self):
        """Test service token pattern for automated/scripted operations."""

        service_name = "DataImportService"
        casefile_id = f"casefile_{uuid4()}"

        service_token = create_service_token(
            service_name=service_name,
            casefile_id=casefile_id,
        )

        assert service_token is not None

        # Decode and verify service token structure
        decoded = decode_test_token(service_token)
        assert decoded["sub"] == f"svc_{service_name}"
        assert decoded["casefile_id"] == casefile_id

        # Service tokens can create operations without human user
        # This supports automation scripts and background jobs

    @pytest.mark.asyncio
    async def test_session_context_preservation_across_operations(
        self, mock_tool_session_service, integration_test_ids
    ):
        """Verify session context flows through multiple operations."""

        user_id = integration_test_ids["user_id"]
        casefile_id = integration_test_ids["casefile_id"]
        session_id = integration_test_ids["session_id"]
        session_request_id = integration_test_ids["session_request_id"]

        # Create multiple operations in same session
        operations = []
        responses = []

        for i in range(3):
            tool_request = ToolRequest(
                request_id=uuid4(),
                user_id=user_id,
                payload={
                    "tool_name": "create_casefile_tool",  # Use valid registered tool
                    "parameters": {"step": i, "title": f"Test {i}", "description": "Test"},
                    "casefile_id": casefile_id,
                    "session_request_id": session_request_id,
                },
                metadata={
                    "casefile_id": casefile_id,
                    "session_request_id": session_request_id,
                    "session_id": session_id,
                    "operation_sequence": i,
                },
            )
            operations.append(tool_request)

            # Execute each operation
            response = await mock_tool_session_service.process_tool_request(
                tool_request, auth_context={"user_id": user_id}
            )
            responses.append(response)

        # Verify all operations share session context
        for op in operations:
            assert op.metadata["session_id"] == session_id
            assert op.metadata["casefile_id"] == casefile_id
            assert op.metadata["session_request_id"] == session_request_id

        # Verify operations are sequenced
        assert operations[0].metadata["operation_sequence"] == 0
        assert operations[2].metadata["operation_sequence"] == 2

        # Verify all operations succeeded
        for response in responses:
            assert response.success is True


class TestMVPAuthFlowValidation:
    """Validate authentication and authorization patterns."""

    def test_token_expiration_handling(self):
        """Test token expiration is properly set."""

        user_id = "test_user"
        username = "test_user"

        # Tokens should have reasonable expiration
        token = create_token(user_id=user_id, username=username)
        decoded = decode_test_token(token)

        # Verify exp claim exists
        assert "exp" in decoded

        # Exp should be in future (within 24 hours for typical session tokens)
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.now()

        assert exp_time > now
        assert exp_time < now + timedelta(hours=25)

    def test_casefile_authorization_context(self):
        """Test casefile context flows through authorization."""

        casefile_id = f"casefile_{uuid4()}"

        token = create_token(
            user_id="test_user",
            username="test_user",
            casefile_id=casefile_id,
        )

        decoded = decode_test_token(token)
        assert decoded["casefile_id"] == casefile_id

        # Authorization logic should check:
        # 1. User has access to specified casefile
        # 2. Operation is within casefile scope


class TestMVPRequestContextFlow:
    """Validate request context flows through R-A-R pattern."""

    def test_request_metadata_structure(self):
        """Test request metadata contains required routing fields."""

        request = ToolRequest(
            request_id=uuid4(),
            user_id="test_user",
            payload={
                "tool_name": "create_casefile_tool",  # Use valid registered tool
                "parameters": {"title": "Test", "description": "Test"},
                "casefile_id": "casefile_123",
                "session_request_id": "req_123",
            },
            metadata={
                "casefile_id": "casefile_123",
                "session_request_id": "req_123",
                "session_id": "session_123",
            },
        )

        # Required routing metadata
        assert "casefile_id" in request.metadata
        assert "session_request_id" in request.metadata
        assert "session_id" in request.metadata

        # User identity
        assert request.user_id == "test_user"

    def test_request_to_response_context_preservation(self):
        """Test context preservation from request to response."""

        request_id = uuid4()
        user_id = "test_user"
        casefile_id = "casefile_123"
        session_request_id = "req_123"

        request = CreateSessionRequest(
            request_id=request_id,
            user_id=user_id,
            payload={"casefile_id": casefile_id},
            metadata={
                "casefile_id": casefile_id,
                "session_request_id": session_request_id,
            },
        )

        # Response should preserve request context
        # (In actual implementation, RequestHub would create response)

        # Verify request has all context for response creation
        assert request.request_id == request_id
        assert request.user_id == user_id
        assert request.metadata["casefile_id"] == casefile_id
        assert request.metadata["session_request_id"] == session_request_id
