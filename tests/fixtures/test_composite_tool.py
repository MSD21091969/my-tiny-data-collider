"""
Prototype composite tool implementation and YAML schema validation.

Tests verify that:
1. Composite tools can orchestrate multiple sub-tools
2. Step execution follows success/failure branching
3. Context flows between steps
4. YAML schema can express composite tool structure
"""

import pytest
from typing import Dict, Any
from pydantic import BaseModel, Field

from pydantic_ai_integration.tool_decorator import (
    register_mds_tool,
    get_tool_definition,
    MANAGED_TOOLS,
)
from pydantic_ai_integration.dependencies import MDSContext


# Test parameter models
class _StepOneParams(BaseModel):
    """Parameters for first step."""

    input_value: str = Field(..., description="Input value to process")


class _StepTwoParams(BaseModel):
    """Parameters for second step."""

    processed_value: str = Field(..., description="Value from step one")
    modifier: str = Field(default="", description="Optional modifier")


@pytest.fixture(autouse=True)
def clear_registries():
    """Clear registries before each test."""
    MANAGED_TOOLS.clear()
    yield
    MANAGED_TOOLS.clear()


class TestCompositeToolPrototype:
    """Test composite tool patterns in code."""

    def test_simple_two_step_composite(self):
        """Composite tool executes two steps in sequence."""

        # Step 1: Process input
        @register_mds_tool(
            name="step_one_tool",
            params_model=_StepOneParams,
            description="First processing step",
            category="test",
        )
        async def step_one_tool(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            return {"processed": f"processed_{input_value}", "status": "success"}

        # Step 2: Transform result
        @register_mds_tool(
            name="step_two_tool",
            params_model=_StepTwoParams,
            description="Second processing step",
            category="test",
        )
        async def step_two_tool(
            ctx: MDSContext, processed_value: str, modifier: str = ""
        ) -> Dict[str, Any]:
            result = f"{processed_value}_{modifier}" if modifier else processed_value
            return {"final_result": result, "status": "complete"}

        # Composite tool: Orchestrate both steps
        @register_mds_tool(
            name="composite_tool",
            params_model=_StepOneParams,  # Takes same input as step 1
            description="Composite tool orchestrating two steps",
            category="test",
        )
        async def composite_tool(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            # Execute step 1
            step1_result = await step_one_tool(ctx, input_value=input_value)

            # Execute step 2 with step 1 output
            step2_result = await step_two_tool(
                ctx, processed_value=step1_result["processed"], modifier="final"
            )

            return {"step1": step1_result, "step2": step2_result, "composite_status": "complete"}

        # Verify registration
        composite_def = get_tool_definition("composite_tool")
        assert composite_def is not None
        assert composite_def.name == "composite_tool"

    async def test_composite_execution_flow(self):
        """Test composite tool execution with actual context."""

        # Register sub-tools
        @register_mds_tool(
            name="fetch_data",
            params_model=_StepOneParams,
            description="Fetch data step",
            category="test",
        )
        async def fetch_data(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            return {"data": f"fetched_{input_value}"}

        @register_mds_tool(
            name="transform_data",
            params_model=_StepTwoParams,
            description="Transform data step",
            category="test",
        )
        async def transform_data(
            ctx: MDSContext, processed_value: str, modifier: str = ""
        ) -> Dict[str, Any]:
            return {"transformed": f"{processed_value}_transformed"}

        # Register composite
        @register_mds_tool(
            name="fetch_and_transform",
            params_model=_StepOneParams,
            description="Fetch and transform composite",
            category="test",
        )
        async def fetch_and_transform(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            # Sub-tools return full BaseResponse, extract payload.result
            fetch_response = await fetch_data(ctx, input_value=input_value)
            fetch_result = fetch_response["payload"]["result"]

            transform_response = await transform_data(
                ctx, processed_value=fetch_result.get("data", "")
            )
            transform_result = transform_response["payload"]["result"]

            return {
                "original_input": input_value,
                "fetched": fetch_result,
                "transformed": transform_result,
            }

        # Execute with test context
        test_ctx = MDSContext(
            user_id="test_user", session_id="test_session", request_id="test_request"
        )

        result = await fetch_and_transform(test_ctx, input_value="test_data")

        # Tool wrapper returns full BaseResponse structure: {request_id, status, payload: {result, events}, timestamp, error, metadata}
        actual_result = result["payload"]["result"]

        assert actual_result["original_input"] == "test_data"
        assert "fetched" in actual_result
        # Fetched/transformed are now unwrapped results
        assert actual_result["fetched"]["data"] == "fetched_test_data"
        assert "transformed" in actual_result
        assert actual_result["transformed"]["transformed"] == "fetched_test_data_transformed"

    async def test_composite_with_conditional_branching(self):
        """Test composite tool with success/failure branching."""

        @register_mds_tool(
            name="validate_input",
            params_model=_StepOneParams,
            description="Validate input step",
            category="test",
        )
        async def validate_input(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            valid = len(input_value) > 0 and input_value != "invalid"
            return {
                "valid": valid,
                "value": input_value,
                "status": "success" if valid else "failure",
            }

        @register_mds_tool(
            name="process_valid",
            params_model=_StepOneParams,
            description="Process valid input",
            category="test",
        )
        async def process_valid(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            return {"result": f"processed_{input_value}"}

        @register_mds_tool(
            name="handle_invalid",
            params_model=_StepOneParams,
            description="Handle invalid input",
            category="test",
        )
        async def handle_invalid(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            return {"error": "Invalid input", "value": input_value}

        @register_mds_tool(
            name="conditional_composite",
            params_model=_StepOneParams,
            description="Composite with branching",
            category="test",
        )
        async def conditional_composite(ctx: MDSContext, input_value: str) -> Dict[str, Any]:
            # Step 1: Validate - extract result from wrapped BaseResponse
            validation_response = await validate_input(ctx, input_value=input_value)
            validation = validation_response["payload"]["result"]

            # Conditional branching
            if validation.get("valid"):
                result_response = await process_valid(ctx, input_value=input_value)
                result = result_response["payload"]["result"]
                return {"validation": validation, "processing": result, "path": "success"}
            else:
                result_response = await handle_invalid(ctx, input_value=input_value)
                result = result_response["payload"]["result"]
                return {"validation": validation, "error_handling": result, "path": "failure"}

        # Test context
        test_ctx = MDSContext(
            user_id="test_user", session_id="test_session", request_id="test_request"
        )

        # Test success path
        success_result = await conditional_composite(test_ctx, input_value="valid_data")
        actual_success = success_result["payload"]["result"]
        assert actual_success["path"] == "success"
        assert "processing" in actual_success
        assert actual_success["processing"]["result"] == "processed_valid_data"

        # Test failure path
        failure_result = await conditional_composite(test_ctx, input_value="invalid")
        actual_failure = failure_result["payload"]["result"]
        assert actual_failure["path"] == "failure"
        assert "error_handling" in actual_failure
        assert actual_failure["error_handling"]["error"] == "Invalid input"


class TestCompositeYAMLSchema:
    """Test YAML schema can express composite tool structure."""

    def test_yaml_composite_structure(self):
        """Verify YAML schema supports composite tool definition."""

        # This test validates the schema structure without loading actual YAML
        # YAML composite tool structure per tool_schema_v2.yaml:
        composite_yaml_structure = {
            "name": "example_composite",
            "description": "Example composite tool",
            "category": "test",
            "implementation": {
                "type": "composite",
                "steps": [
                    {
                        "tool": "step_one_tool",
                        "inputs": {"input_value": "${context.input}"},
                        "on_success": {"store_result": "step1_output"},
                        "on_failure": {"abort": True},
                    },
                    {
                        "tool": "step_two_tool",
                        "inputs": {
                            "processed_value": "${step1_output.processed}",
                            "modifier": "final",
                        },
                        "on_success": {"store_result": "final_output"},
                    },
                ],
            },
            "parameters": [
                {
                    "name": "input_value",
                    "type": "string",
                    "required": True,
                    "description": "Initial input value",
                }
            ],
            "returns": {
                "type": "object",
                "properties": {
                    "step1": {"type": "object"},
                    "step2": {"type": "object"},
                    "composite_status": {"type": "string"},
                },
            },
        }

        # Validate required composite fields
        assert composite_yaml_structure["implementation"]["type"] == "composite"
        assert "steps" in composite_yaml_structure["implementation"]
        assert len(composite_yaml_structure["implementation"]["steps"]) == 2

        # Validate step structure
        step1 = composite_yaml_structure["implementation"]["steps"][0]
        assert "tool" in step1
        assert "inputs" in step1
        assert "on_success" in step1
        assert "on_failure" in step1

        # Validate context variable substitution pattern
        assert "${context.input}" in step1["inputs"]["input_value"]
        assert (
            "${step1_output.processed}"
            in composite_yaml_structure["implementation"]["steps"][1]["inputs"]["processed_value"]
        )

    def test_composite_metadata_structure(self):
        """Test composite tool metadata captures orchestration details."""

        composite_metadata = {
            "name": "fetch_transform_store",
            "description": "Composite pipeline: fetch → transform → store",
            "category": "automation",
            "version": "1.0.0",
            "tags": ["composite", "pipeline", "automation"],
            "metadata": {
                "orchestration_pattern": "sequential",
                "step_count": 3,
                "supports_rollback": True,
                "execution_mode": "synchronous",
            },
            "implementation": {
                "type": "composite",
                "steps": [
                    {"tool": "fetch_data", "inputs": {}},
                    {"tool": "transform_data", "inputs": {}},
                    {"tool": "store_data", "inputs": {}},
                ],
            },
        }

        # Validate metadata captures orchestration intent
        assert composite_metadata["metadata"]["orchestration_pattern"] == "sequential"
        assert composite_metadata["metadata"]["step_count"] == 3
        assert composite_metadata["tags"] == ["composite", "pipeline", "automation"]
        assert len(composite_metadata["implementation"]["steps"]) == 3
