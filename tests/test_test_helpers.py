"""Test the new test helpers functionality."""
import pytest
import asyncio
from tests.test_helpers import ToolTestHelper, tool_test_context, run_tool_test_scenario, execute_casefile_crud_operations


class TestTestHelpers:
    """Test the test helper utilities."""

    @pytest.fixture
    async def helper(self):
        """Provide a test helper instance."""
        async with tool_test_context() as helper:
            yield helper

    @pytest.mark.asyncio
    async def test_helper_creation(self, helper: ToolTestHelper):
        """Test that the helper can be created and has expected methods."""
        assert hasattr(helper, 'create_test_casefile')
        assert hasattr(helper, 'create_test_session')
        assert hasattr(helper, 'execute_tool_via_session')
        assert hasattr(helper, 'cleanup_test_resources')

    @pytest.mark.asyncio
    async def test_create_test_casefile(self, helper: ToolTestHelper):
        """Test creating a test casefile."""
        casefile_id = await helper.create_test_casefile(
            title="Helper Test Casefile",
            description="Testing the helper functionality"
        )

        assert casefile_id is not None
        assert isinstance(casefile_id, str)
        assert casefile_id.startswith("cf_")

    @pytest.mark.asyncio
    async def test_create_test_session(self, helper: ToolTestHelper):
        """Test creating a test session."""
        session_id = await helper.create_test_session()

        assert session_id is not None
        assert isinstance(session_id, str)
        assert session_id.startswith("ts_")

    @pytest.mark.asyncio
    async def test_casefile_session_pair_creation(self, helper: ToolTestHelper):
        """Test creating a casefile-session pair."""
        casefile_id, session_id = await helper.create_test_casefile(), await helper.create_test_session()

        assert casefile_id.startswith("cf_")
        assert session_id.startswith("ts_")

    @pytest.mark.asyncio
    async def test_execute_tool_via_session(self, helper: ToolTestHelper):
        """Test executing a tool via session."""
        # Create test resources
        casefile_id = await helper.create_test_casefile()
        session_id = await helper.create_test_session(casefile_id=casefile_id)

        # Execute a simple tool
        result = await helper.execute_tool_via_session(
            "get_casefile_tool",
            {"casefile_id": casefile_id},
            session_id
        )

        assert result is not None
        assert "casefile" in result
        assert result["casefile"]["metadata"]["title"] == "Test Casefile"

    @pytest.mark.asyncio
    async def test_crud_operations_helper(self, helper: ToolTestHelper):
        """Test the CRUD operations helper function."""
        # Create test session
        session_id = await helper.create_test_session()

        # Execute CRUD operations
        results = await execute_casefile_crud_operations(helper, session_id)

        # Verify all operations completed
        assert "create" in results
        assert "get" in results
        assert "update" in results
        assert "list" in results
        assert "delete" in results

        # Verify create returned a casefile_id
        assert "casefile_id" in results["create"]

        # Verify get returned casefile data
        assert "casefile" in results["get"]

        # Verify update returned updated data
        assert "casefile" in results["update"]

        # Verify list returned casefiles array
        assert "casefiles" in results["list"]
        assert isinstance(results["list"]["casefiles"], list)

        # Verify delete returned casefile_id
        assert "casefile_id" in results["delete"]

    @pytest.mark.asyncio
    async def test_run_tool_test_scenario(self):
        """Test the scenario runner function."""
        async def simple_test(helper: ToolTestHelper):
            casefile_id = await helper.create_test_casefile(title="Scenario Test")
            return {"casefile_id": casefile_id}

        result = await run_tool_test_scenario("Simple Test", simple_test)

        assert result["scenario"] == "Simple Test"
        assert result["status"] == "success"
        assert "casefile_id" in result["result"]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])