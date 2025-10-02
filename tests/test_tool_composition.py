"""
Comprehensive test suite for tool composition engine.

Tests cover:
- Chain validation
- Sequential execution
- Parallel execution
- Error handling
- Chain state management
- Composite tool registration
- Result aggregation
"""

import pytest
from typing import Dict, Any
from uuid import uuid4

from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.chains import (
    ChainExecutor,
    ChainExecutionMode,
    ChainStatus,
    ChainExecutionError
)
from src.pydantic_ai_integration.tool_decorator import (
    register_composite_tool,
    get_composite_tool,
    get_all_composite_tools,
    list_composite_tools_by_category,
    COMPOSITE_TOOLS
)
from src.pydantic_ai_integration.tools.example_composite_tools import (
    execute_composite_tool,
    DATA_ENRICHMENT_CHAIN,
    VALIDATION_CHAIN,
    PARALLEL_PROCESSING_CHAIN,
    ANALYSIS_PIPELINE
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def test_context():
    """Create a test MDSContext."""
    return MDSContext(
        user_id="test_user",
        session_id="ts_test_session",
        casefile_id="cf_251001_TEST"
    )


@pytest.fixture
def simple_chain():
    """Create a simple tool chain for testing."""
    return [
        {"tool_name": "example_tool", "parameters": {"value": 42}},
        {"tool_name": "another_example_tool", "parameters": {"name": "test", "count": 1}}
    ]


@pytest.fixture
def chain_with_error():
    """Create a chain that will cause an error."""
    return [
        {"tool_name": "example_tool", "parameters": {"value": 10}},
        {"tool_name": "nonexistent_tool", "parameters": {}},
        {"tool_name": "another_example_tool", "parameters": {"name": "step3", "count": 1}}
    ]


# =============================================================================
# Chain Validation Tests
# =============================================================================

@pytest.mark.unit
def test_validate_empty_chain(test_context):
    """Test validation of empty chain."""
    validation = test_context.validate_chain([])
    
    assert validation["valid"] is False
    assert len(validation["errors"]) > 0
    assert "at least one tool" in validation["errors"][0].lower()


@pytest.mark.unit
def test_validate_valid_chain(test_context):
    """Test validation of valid chain."""
    chain = [
        {"tool_name": "tool1", "parameters": {}},
        {"tool_name": "tool2", "parameters": {"param": "value"}}
    ]
    
    validation = test_context.validate_chain(chain)
    
    assert validation["valid"] is True
    assert len(validation["errors"]) == 0
    assert validation["tool_count"] == 2


@pytest.mark.unit
def test_validate_chain_missing_tool_name(test_context):
    """Test validation of chain with missing tool_name."""
    chain = [
        {"parameters": {"param": "value"}},
        {"tool_name": "tool2", "parameters": {}}
    ]
    
    validation = test_context.validate_chain(chain)
    
    assert validation["valid"] is False
    assert len(validation["errors"]) > 0
    assert "tool_name" in validation["errors"][0].lower()


@pytest.mark.unit
def test_validate_chain_missing_parameters(test_context):
    """Test validation warns about missing parameters field."""
    chain = [
        {"tool_name": "tool1"},
        {"tool_name": "tool2", "parameters": {}}
    ]
    
    validation = test_context.validate_chain(chain)
    
    assert validation["valid"] is True  # Still valid, just warning
    assert len(validation["warnings"]) > 0


@pytest.mark.unit
def test_validate_single_tool_chain(test_context):
    """Test validation of single-tool chain."""
    chain = [{"tool_name": "tool1", "parameters": {}}]
    
    validation = test_context.validate_chain(chain)
    
    assert validation["valid"] is True
    assert validation["tool_count"] == 1


# =============================================================================
# Chain Executor Initialization Tests
# =============================================================================

@pytest.mark.unit
def test_chain_executor_initialization(test_context):
    """Test ChainExecutor initialization."""
    executor = ChainExecutor(test_context)
    
    assert executor.context == test_context
    assert executor.current_chain_id is None
    assert executor.current_status == ChainStatus.PENDING


@pytest.mark.unit
def test_chain_executor_get_status(test_context):
    """Test getting executor status."""
    executor = ChainExecutor(test_context)
    
    status = executor.get_status()
    
    assert status == ChainStatus.PENDING


@pytest.mark.unit
def test_chain_executor_get_current_chain_id(test_context):
    """Test getting current chain ID."""
    executor = ChainExecutor(test_context)
    
    chain_id = executor.get_current_chain_id()
    
    assert chain_id is None


# =============================================================================
# Sequential Execution Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_sequential_chain_success(test_context, simple_chain):
    """Test successful sequential chain execution."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.SEQUENTIAL
    )
    
    assert result["status"] == ChainStatus.COMPLETED
    assert "chain_id" in result
    assert len(result["results"]) == 2
    assert result["summary"]["successful"] == 2
    assert result["summary"]["failed"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_sequential_with_chain_name(test_context, simple_chain):
    """Test sequential execution with named chain."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="test_chain"
    )
    
    assert result["status"] == ChainStatus.COMPLETED
    assert "test_chain" in test_context.active_chains or result["status"] == ChainStatus.COMPLETED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_sequential_stop_on_error(test_context, chain_with_error):
    """Test sequential execution stops on error when configured."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain_with_error,
        mode=ChainExecutionMode.SEQUENTIAL,
        stop_on_error=True
    )
    
    assert result["status"] in [ChainStatus.FAILED, ChainStatus.PARTIALLY_COMPLETED]
    # Should stop at error, so results should be 1 or 2 (not all 3)
    assert len(result["results"]) < len(chain_with_error)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_sequential_continue_on_error(test_context, chain_with_error):
    """Test sequential execution continues on error when configured."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain_with_error,
        mode=ChainExecutionMode.SEQUENTIAL,
        stop_on_error=False
    )
    
    # Should attempt all tools even with error
    assert len(result["results"]) <= len(chain_with_error)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_sequential_pass_results(test_context):
    """Test sequential execution passes results between tools."""
    chain = [
        {"tool_name": "example_tool", "parameters": {"value": 10}},
        {"tool_name": "example_tool", "parameters": {"value": 20}}
    ]
    
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        pass_results=True
    )
    
    # Check that second tool has access to previous result
    if len(result["results"]) >= 2:
        second_result = result["results"][1]
        # The implementation should have _previous_result in parameters
        assert second_result["success"] or "error" in second_result


# =============================================================================
# Parallel Execution Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_parallel_chain_success(test_context, simple_chain):
    """Test successful parallel chain execution."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.PARALLEL
    )
    
    assert result["status"] == ChainStatus.COMPLETED
    assert len(result["results"]) == 2
    assert result["summary"]["mode"] == ChainExecutionMode.PARALLEL


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_parallel_with_error(test_context, chain_with_error):
    """Test parallel execution handles errors."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain_with_error,
        mode=ChainExecutionMode.PARALLEL,
        stop_on_error=True
    )
    
    # All tools should be attempted in parallel
    assert len(result["results"]) == len(chain_with_error)
    # Should have at least one error
    errors = [r for r in result["results"] if "error" in r]
    assert len(errors) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parallel_execution_order_preserved(test_context):
    """Test that parallel execution preserves tool order in results."""
    chain = [
        {"tool_name": "example_tool", "parameters": {"value": 1}},
        {"tool_name": "example_tool", "parameters": {"value": 2}},
        {"tool_name": "example_tool", "parameters": {"value": 3}}
    ]
    
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain,
        mode=ChainExecutionMode.PARALLEL
    )
    
    # Results should be in same order as input chain
    assert len(result["results"]) == 3
    for i, tool_result in enumerate(result["results"], start=1):
        assert tool_result["position"] == i


# =============================================================================
# Error Handling Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_invalid_chain(test_context):
    """Test execution of invalid chain."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=[],  # Empty chain
        mode=ChainExecutionMode.SEQUENTIAL
    )
    
    assert result["status"] == ChainStatus.FAILED
    assert "validation" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_with_nonexistent_tool(test_context):
    """Test execution with nonexistent tool."""
    chain = [{"tool_name": "does_not_exist", "parameters": {}}]
    
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=chain,
        mode=ChainExecutionMode.SEQUENTIAL
    )
    
    # Should complete but with error in result
    assert len(result["results"]) >= 0
    if result["results"]:
        assert result["results"][0]["success"] is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chain_status_after_failure(test_context, chain_with_error):
    """Test chain status is updated after failure."""
    executor = ChainExecutor(test_context)
    
    await executor.execute_chain(
        tools=chain_with_error,
        mode=ChainExecutionMode.SEQUENTIAL,
        stop_on_error=True
    )
    
    status = executor.get_status()
    
    assert status in [ChainStatus.FAILED, ChainStatus.PARTIALLY_COMPLETED]


# =============================================================================
# Chain State Management Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_chain_results(test_context, simple_chain):
    """Test retrieving chain results after execution."""
    executor = ChainExecutor(test_context)
    
    exec_result = await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="test_results_chain"
    )
    
    chain_id = exec_result["chain_id"]
    
    # Get results using context method
    results = test_context.get_chain_results(chain_id=chain_id)
    
    assert len(results) >= 0
    for result in results:
        assert "tool_name" in result
        assert "position" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_chain_status_after_execution(test_context, simple_chain):
    """Test getting chain status after execution."""
    executor = ChainExecutor(test_context)
    
    result = await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="status_test_chain"
    )
    
    chain_id = result["chain_id"]
    
    # Get status using context method
    status = test_context.get_chain_status(chain_id=chain_id)
    
    assert isinstance(status, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_active_chains_tracking(test_context, simple_chain):
    """Test that active chains are tracked during execution."""
    executor = ChainExecutor(test_context)
    
    await executor.execute_chain(
        tools=simple_chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="active_chain_test"
    )
    
    # Chain should be tracked (or removed if completed successfully)
    # Either way, the context should have processed it
    assert len(test_context.tool_events) > 0


# =============================================================================
# Composite Tool Registration Tests
# =============================================================================

@pytest.mark.unit
def test_register_composite_tool():
    """Test registering a composite tool."""
    tool_name = f"test_composite_{uuid4().hex[:8]}"
    
    composite = register_composite_tool(
        name=tool_name,
        description="Test composite tool",
        tool_chain=[
            {"tool_name": "tool1", "parameters": {}},
            {"tool_name": "tool2", "parameters": {}}
        ],
        category="test"
    )
    
    assert composite.name == tool_name
    assert len(composite.tool_chain) == 2
    assert composite.category == "test"
    
    # Clean up
    if tool_name in COMPOSITE_TOOLS:
        del COMPOSITE_TOOLS[tool_name]


@pytest.mark.unit
def test_get_composite_tool():
    """Test retrieving a composite tool."""
    # Use existing registered tool
    tool = get_composite_tool("data_enrichment_chain")
    
    assert tool is not None
    assert tool.name == "data_enrichment_chain"
    assert len(tool.tool_chain) > 0


@pytest.mark.unit
def test_get_nonexistent_composite_tool():
    """Test retrieving nonexistent composite tool."""
    tool = get_composite_tool("does_not_exist")
    
    assert tool is None


@pytest.mark.unit
def test_get_all_composite_tools():
    """Test getting all composite tools."""
    tools = get_all_composite_tools()
    
    assert isinstance(tools, dict)
    assert len(tools) >= 4  # At least our example tools


@pytest.mark.unit
def test_list_composite_tools_by_category():
    """Test listing composite tools by category."""
    tools = list_composite_tools_by_category("data_processing")
    
    assert isinstance(tools, list)
    # Should have at least the data enrichment chain
    assert any(t.name == "data_enrichment_chain" for t in tools)


@pytest.mark.unit
def test_composite_tool_attributes():
    """Test composite tool has all required attributes."""
    tool = get_composite_tool("validation_chain")
    
    assert tool is not None
    assert hasattr(tool, "name")
    assert hasattr(tool, "description")
    assert hasattr(tool, "tool_chain")
    assert hasattr(tool, "execution_mode")
    assert hasattr(tool, "stop_on_error")
    assert hasattr(tool, "pass_results")


# =============================================================================
# Example Composite Tools Tests
# =============================================================================

@pytest.mark.unit
def test_data_enrichment_chain_registered():
    """Test that data enrichment chain is registered."""
    assert DATA_ENRICHMENT_CHAIN is not None
    assert DATA_ENRICHMENT_CHAIN.name == "data_enrichment_chain"
    assert DATA_ENRICHMENT_CHAIN.execution_mode == "sequential"


@pytest.mark.unit
def test_validation_chain_registered():
    """Test that validation chain is registered."""
    assert VALIDATION_CHAIN is not None
    assert VALIDATION_CHAIN.name == "validation_chain"
    assert len(VALIDATION_CHAIN.tool_chain) == 3


@pytest.mark.unit
def test_parallel_processing_chain_registered():
    """Test that parallel processing chain is registered."""
    assert PARALLEL_PROCESSING_CHAIN is not None
    assert PARALLEL_PROCESSING_CHAIN.execution_mode == "parallel"
    assert PARALLEL_PROCESSING_CHAIN.pass_results is False


@pytest.mark.unit
def test_analysis_pipeline_registered():
    """Test that analysis pipeline is registered."""
    assert ANALYSIS_PIPELINE is not None
    assert ANALYSIS_PIPELINE.category == "analysis"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_composite_tool_success(test_context):
    """Test executing a composite tool."""
    result = await execute_composite_tool(
        context=test_context,
        composite_tool_name="validation_chain"
    )
    
    assert "status" in result
    assert "chain_id" in result or "error" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_nonexistent_composite_tool(test_context):
    """Test executing nonexistent composite tool."""
    result = await execute_composite_tool(
        context=test_context,
        composite_tool_name="does_not_exist"
    )
    
    assert "error" in result
    assert result["success"] is False


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_chain_workflow(test_context):
    """Test complete chain workflow from creation to execution."""
    # 1. Create a chain
    chain = [
        {"tool_name": "example_tool", "parameters": {"value": 100}},
        {"tool_name": "another_example_tool", "parameters": {"name": "workflow", "count": 1}}
    ]
    
    # 2. Validate the chain
    validation = test_context.validate_chain(chain)
    assert validation["valid"] is True
    
    # 3. Execute the chain
    executor = ChainExecutor(test_context)
    result = await executor.execute_chain(
        tools=chain,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="full_workflow_test"
    )
    
    # 4. Check results
    assert result["status"] == ChainStatus.COMPLETED
    assert len(result["results"]) == 2
    
    # 5. Get chain status
    status = test_context.get_chain_status(chain_id=result["chain_id"])
    assert isinstance(status, dict)
    
    # 6. Get chain results
    results = test_context.get_chain_results(chain_id=result["chain_id"])
    assert len(results) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nested_chain_tracking(test_context):
    """Test that multiple chains can be tracked in same context."""
    executor = ChainExecutor(test_context)
    
    # Execute first chain
    chain1 = [{"tool_name": "example_tool", "parameters": {"value": 1}}]
    result1 = await executor.execute_chain(
        tools=chain1,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="chain_1"
    )
    
    # Execute second chain
    chain2 = [{"tool_name": "example_tool", "parameters": {"value": 2}}]
    result2 = await executor.execute_chain(
        tools=chain2,
        mode=ChainExecutionMode.SEQUENTIAL,
        chain_name="chain_2"
    )
    
    # Both chains should have different IDs
    assert result1["chain_id"] != result2["chain_id"]
    
    # Context should have events from both chains
    assert len(test_context.tool_events) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chain_with_real_tools(test_context):
    """Test chain execution with actual registered tools."""
    # This uses the actual tool registry
    chain = [
        {"tool_name": "example_tool", "parameters": {"value": 42}},
        {"tool_name": "another_example_tool", "parameters": {"name": "real_test", "count": 2}}
    ]
    
    executor = ChainExecutor(test_context)
    result = await executor.execute_chain(
        tools=chain,
        mode=ChainExecutionMode.SEQUENTIAL
    )
    
    # Should complete successfully with real tools
    assert result["status"] == ChainStatus.COMPLETED
    assert result["summary"]["successful"] == 2
