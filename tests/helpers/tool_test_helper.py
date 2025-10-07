"""
Consolidated test helpers for tool testing.

Provides utilities for testing MDS tools with reduced boilerplate.
Consolidated from multiple test helper files into single, clean interface.
"""
import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
from contextlib import asynccontextmanager

from pydantic_models.operations.casefile_ops import CreateCasefileRequest, CreateCasefilePayload
from pydantic_models.operations.tool_session_ops import CreateSessionRequest, CreateSessionPayload
from pydantic_models.operations.tool_execution_ops import ToolRequest, ToolResponse
from casefileservice.service import CasefileService
from tool_sessionservice.service import ToolSessionService
from pydantic_ai_integration.dependencies import MDSContext


class ToolTestHelper:
    """Helper class for testing MDS tools with reduced boilerplate."""

    def __init__(self, casefile_service: CasefileService, tool_session_service: ToolSessionService):
        self.casefile_service = casefile_service
        self.tool_session_service = tool_session_service
        self._cleanup_items: List[Dict[str, Any]] = []

    async def create_test_casefile(
        self,
        user_id: str = "test_user_123",
        title: str = "Test Casefile",
        description: str = "Test casefile for tool testing",
        tags: Optional[List[str]] = None
    ) -> str:
        """Create a test casefile and register it for cleanup.

        Args:
            user_id: User ID for the casefile owner
            title: Casefile title
            description: Casefile description
            tags: Optional tags for the casefile

        Returns:
            casefile_id: The ID of the created casefile
        """
        if tags is None:
            tags = ["test", "auto-generated"]

        request = CreateCasefileRequest(
            user_id=user_id,
            operation="create_casefile",
            payload=CreateCasefilePayload(
                title=title,
                description=description,
                tags=tags
            )
        )

        response = await self.casefile_service.create_casefile(request)
        casefile_id = response.payload.casefile_id

        # Register for cleanup
        self._cleanup_items.append({
            "type": "casefile",
            "casefile_id": casefile_id,
            "user_id": user_id
        })

        return casefile_id

    async def create_test_session(
        self,
        user_id: str = "test_user_123",
        casefile_id: str = None
    ) -> str:
        """Create a test session and register it for cleanup.

        Args:
            user_id: User ID for the session owner
            casefile_id: Optional casefile ID to link the session to

        Returns:
            session_id: The ID of the created session
        """
        if casefile_id is None:
            # Create a test casefile if none provided
            casefile_id = await self.create_test_casefile(user_id=user_id)

        request = CreateSessionRequest(
            user_id=user_id,
            operation="create_session",
            payload=CreateSessionPayload(
                casefile_id=casefile_id
            )
        )

        response = await self.tool_session_service.create_session(request)
        session_id = response.payload.session_id

        # Register for cleanup
        self._cleanup_items.append({
            "type": "session",
            "session_id": session_id,
            "user_id": user_id
        })

        return session_id

    async def execute_tool_via_session(
        self,
        tool_name: str,
        params: Dict[str, Any],
        session_id: str,
        user_id: str = "test_user_123"
    ) -> Dict[str, Any]:
        """Execute a tool via a session with proper context setup.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            session_id: Session ID to use
            user_id: User ID for the context

        Returns:
            Tool execution result
        """
        # Import here to avoid circular imports
        from pydantic_ai_integration.tools import MANAGED_TOOLS

        if tool_name not in MANAGED_TOOLS:
            raise ValueError(f"Tool '{tool_name}' not found in MANAGED_TOOLS")

        tool = MANAGED_TOOLS[tool_name]

        # Create MDS context
        ctx = MDSContext(
            user_id=user_id,
            session_id=session_id,
            tool_name=tool_name,
            request_id=f"test_{tool_name}_{session_id}",
            permissions=["casefiles:read", "casefiles:write", "casefiles:delete"],
            metadata={"test_mode": True}
        )

        # Execute the tool
        try:
            result = await tool.implementation(ctx, **params)
            return result
        except Exception as e:
            # Log the error for debugging
            print(f"Tool execution failed: {tool_name} with params {params}")
            raise e

    async def cleanup_test_resources(self):
        """Clean up all test resources created during testing."""
        # Clean up in reverse order (sessions before casefiles)
        for item in reversed(self._cleanup_items):
            try:
                if item["type"] == "session":
                    # Sessions are typically cleaned up automatically
                    pass
                elif item["type"] == "casefile":
                    # Delete the casefile
                    await self._delete_casefile(item["casefile_id"], item["user_id"])
            except Exception as e:
                print(f"Warning: Failed to cleanup {item}: {e}")

        self._cleanup_items.clear()

    async def _delete_casefile(self, casefile_id: str, user_id: str):
        """Delete a casefile (internal cleanup method)."""
        # Use the delete tool if available, otherwise direct service call
        try:
            session_id = await self.create_test_session(user_id=user_id)
            await self.execute_tool_via_session(
                "delete_casefile_tool",
                {"casefile_id": casefile_id, "confirm_deletion": True},
                session_id,
                user_id
            )
        except Exception:
            # Fallback to direct service call
            from pydantic_models.operations.casefile_ops import DeleteCasefileRequest, DeleteCasefilePayload

            request = DeleteCasefileRequest(
                user_id=user_id,
                operation="delete_casefile",
                payload=DeleteCasefilePayload(
                    casefile_id=casefile_id,
                    confirm_deletion=True
                )
            )

            try:
                await self.casefile_service.delete_casefile(request)
            except Exception as e:
                print(f"Warning: Failed to delete casefile {casefile_id}: {e}")


@asynccontextmanager
async def tool_test_context() -> AsyncGenerator[ToolTestHelper, None]:
    """Context manager for tool testing with automatic cleanup.

    Usage:
        async with tool_test_context() as helper:
            casefile_id = await helper.create_test_casefile()
            session_id = await helper.create_test_session(casefile_id=casefile_id)
            result = await helper.execute_tool_via_session("tool_name", params, session_id)
        # Cleanup happens automatically
    """
    # Initialize services (in a real app, these would be injected)
    casefile_service = CasefileService()
    tool_session_service = ToolSessionService()

    helper = ToolTestHelper(casefile_service, tool_session_service)

    try:
        yield helper
    finally:
        await helper.cleanup_test_resources()


async def run_tool_test_scenario(
    scenario_name: str,
    test_func: callable,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Run a tool test scenario with proper setup and cleanup.

    Args:
        scenario_name: Name of the test scenario
        test_func: Async function to run the test
        *args, **kwargs: Arguments to pass to test_func

    Returns:
        Test results dictionary
    """
    print(f"=== Running Scenario: {scenario_name} ===")

    async with tool_test_context() as helper:
        try:
            result = await test_func(helper, *args, **kwargs)
            print(f"✓ Scenario '{scenario_name}' completed successfully")
            return {
                "scenario": scenario_name,
                "status": "success",
                "result": result
            }
        except Exception as e:
            print(f"✗ Scenario '{scenario_name}' failed: {e}")
            return {
                "scenario": scenario_name,
                "status": "failed",
                "error": str(e)
            }


# Convenience functions for common test patterns

async def create_casefile_session_pair(
    helper: ToolTestHelper,
    user_id: str = "test_user_123",
    casefile_title: str = "Test Casefile",
    casefile_description: str = "Test casefile for tool testing"
) -> tuple[str, str]:
    """Create a casefile-session pair for testing.

    Returns:
        tuple: (casefile_id, session_id)
    """
    casefile_id = await helper.create_test_casefile(
        user_id=user_id,
        title=casefile_title,
        description=casefile_description
    )
    session_id = await helper.create_test_session(user_id=user_id, casefile_id=casefile_id)
    return casefile_id, session_id


async def execute_casefile_crud_operations(
    helper: ToolTestHelper,
    session_id: str,
    user_id: str = "test_user_123"
) -> Dict[str, Any]:
    """Execute all CRUD operations on casefiles for comprehensive testing.

    Returns:
        Dictionary with results of all operations
    """
    results = {}

    # Create
    create_params = {
        "title": "CRUD Test Casefile",
        "description": "Testing all CRUD operations",
        "tags": ["test", "crud"]
    }
    results["create"] = await helper.execute_tool_via_session(
        "create_casefile_tool", create_params, session_id, user_id
    )
    casefile_id = results["create"]["casefile_id"]

    # Get
    results["get"] = await helper.execute_tool_via_session(
        "get_casefile_tool", {"casefile_id": casefile_id}, session_id, user_id
    )

    # Update
    update_params = {
        "casefile_id": casefile_id,
        "title": "Updated CRUD Test Casefile",
        "description": "Updated description",
        "tags": ["test", "crud", "updated"]
    }
    results["update"] = await helper.execute_tool_via_session(
        "update_casefile_tool", update_params, session_id, user_id
    )

    # List (should include our casefile)
    results["list"] = await helper.execute_tool_via_session(
        "list_casefiles_tool", {"owner_user_id": user_id, "limit": 20}, session_id, user_id
    )

    # Delete
    results["delete"] = await helper.execute_tool_via_session(
        "delete_casefile_tool", {"casefile_id": casefile_id, "confirm_deletion": True}, session_id, user_id
    )

    return results