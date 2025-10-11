"""
Fixture tests for ToolDec parameter inheritance from methods.

TIER 1 #3 validation: Verify tools inherit parameters correctly from methods.

Covers:
1. Tool parameters extracted from params_model
2. Tools reference methods via method_name
3. Registry consistency for tool/method lookups
4. Parameter alignment for YAML-generated tools
"""

import pytest
from pydantic import BaseModel, Field

from pydantic_ai_integration.tool_decorator import (
    register_mds_tool,
    get_tool_definition,
    MANAGED_TOOLS,
)
from pydantic_ai_integration.method_registry import (
    MANAGED_METHODS,
    register_method,
    get_method_definition,
)
from pydantic_ai_integration.method_definition import ManagedMethodDefinition
from pydantic_ai_integration.dependencies import MDSContext


# Param models (avoid Test prefix for pytest)
class MethodParams(BaseModel):
    """Parameters for test method."""

    title: str = Field(..., description="Title field")
    description: str = Field(default="", description="Description field")
    count: int = Field(default=1, description="Count field", ge=1, le=100)


class ToolParams(BaseModel):
    """Parameters for test tool."""

    name: str = Field(..., description="Name field")
    value: str = Field(default="default", description="Value field")


@pytest.fixture(autouse=True)
def clear_registries():
    """Clear registries before each test."""
    MANAGED_TOOLS.clear()
    MANAGED_METHODS.clear()


class TestParameterInheritance:
    """Test parameter extraction and inheritance."""

    def test_tool_extracts_parameters_from_params_model(self):
        """Tool decorator extracts parameters from params_model."""

        @register_mds_tool(
            name="param_tool",
            params_model=ToolParams,
            description="Tool with param model",
            category="test",
        )
        async def param_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("param_tool")
        assert tool_def is not None
        assert len(tool_def.parameters) == 2

        param_names = [p.name for p in tool_def.parameters]
        assert "name" in param_names
        assert "value" in param_names

        name_param = next(p for p in tool_def.parameters if p.name == "name")
        assert name_param.required is True

        value_param = next(p for p in tool_def.parameters if p.name == "value")
        assert value_param.required is False
        assert value_param.default_value == "default"

    def test_tool_references_method_via_method_name(self):
        """Tool can reference method via method_name field."""

        # Register method manually
        method_def = ManagedMethodDefinition(
            name="test_method",
            description="Test method for inheritance",
            domain="test",
            subdomain="inheritance",
            capability="create",
            complexity="atomic",
            maturity="stable",
            integration_tier="internal",
            implementation_class="TestService",
            implementation_method="test_method",
            request_model_class=None,
            response_model_class=None,
        )
        register_method("test_method", method_def)

        # Register tool referencing method
        @register_mds_tool(
            name="method_tool",
            params_model=MethodParams,
            description="Tool referencing method",
            category="test",
            method_name="test_method",
        )
        async def method_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("method_tool")
        assert tool_def is not None
        assert tool_def.method_name == "test_method"

        # Verify method exists in registry
        method = get_method_definition("test_method")
        assert method is not None
        assert method.name == "test_method"

    def test_parameter_constraints_inherited(self):
        """Parameter constraints from Pydantic model are preserved."""

        @register_mds_tool(
            name="constrained_tool",
            params_model=MethodParams,
            description="Tool with constrained params",
            category="test",
        )
        async def constrained_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("constrained_tool")
        count_param = next(p for p in tool_def.parameters if p.name == "count")

        # Constraints from Field(ge=1, le=100)
        assert count_param.min_value == 1
        assert count_param.max_value == 100

    def test_validation_with_params_model(self):
        """validate_params returns validated Pydantic model."""

        @register_mds_tool(
            name="validated_tool",
            params_model=MethodParams,
            description="Tool with validation",
            category="test",
        )
        async def validated_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("validated_tool")

        # Valid params
        valid_params = {"title": "Test", "description": "Desc", "count": 50}
        validated = tool_def.validate_params(valid_params)
        assert validated.title == "Test"
        assert validated.count == 50

        # Invalid params (count out of range)
        from pydantic import ValidationError

        invalid_params = {"title": "Test", "count": 200}
        with pytest.raises(ValidationError):
            tool_def.validate_params(invalid_params)


class TestRegistryConsistency:
    """Test registry operations and lookups."""

    def test_tool_registration_updates_registry(self):
        """Registering tool updates MANAGED_TOOLS."""
        assert len(MANAGED_TOOLS) == 0

        @register_mds_tool(
            name="registry_tool",
            params_model=ToolParams,
            description="Tool for registry test",
            category="test",
        )
        async def registry_tool(ctx: MDSContext, **kwargs):
            return kwargs

        assert len(MANAGED_TOOLS) == 1
        assert "registry_tool" in MANAGED_TOOLS

    def test_get_tool_definition_returns_complete_metadata(self):
        """get_tool_definition returns full ManagedToolDefinition."""

        @register_mds_tool(
            name="metadata_tool",
            params_model=ToolParams,
            description="Tool with metadata",
            category="workspace",
        )
        async def metadata_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("metadata_tool")
        assert tool_def.name == "metadata_tool"
        assert tool_def.description == "Tool with metadata"
        assert tool_def.category == "workspace"
        assert tool_def.params_model == ToolParams
        assert len(tool_def.parameters) == 2

    def test_nonexistent_tool_returns_none(self):
        """get_tool_definition returns None for nonexistent tool."""
        tool_def = get_tool_definition("nonexistent_tool")
        assert tool_def is None


class TestYAMLGeneratedTools:
    """Test YAML-generated tool structure alignment."""

    def test_yaml_tool_parameter_structure(self):
        """YAML-loaded tools have correct parameter structure."""
        from pydantic_ai_integration.tool_definition import ToolParameterDef

        # Simulate YAML-generated tool parameter
        param_def = ToolParameterDef(
            name="title",
            param_type="string",
            required=True,
            description="Title field",
        )

        assert param_def.name == "title"
        assert param_def.param_type == "string"
        assert param_def.required is True
        assert param_def.description == "Title field"


class TestParameterExtractionEdgeCases:
    """Test edge cases in parameter extraction."""

    def test_optional_fields_with_defaults(self):
        """Optional fields with defaults have correct metadata."""

        class OptionalParams(BaseModel):
            required_field: str
            optional_with_default: str = "default_value"
            optional_without_default: str = None

        @register_mds_tool(
            name="optional_tool",
            params_model=OptionalParams,
            description="Tool with optional params",
            category="test",
        )
        async def optional_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("optional_tool")
        params_by_name = {p.name: p for p in tool_def.parameters}

        assert params_by_name["required_field"].required is True
        assert params_by_name["optional_with_default"].required is False
        assert params_by_name["optional_with_default"].default_value == "default_value"
        assert params_by_name["optional_without_default"].required is False


class TestToolExecutionWithInheritedParams:
    """Test tool execution with parameter validation."""

    @pytest.mark.asyncio
    async def test_execute_tool_with_validated_params(self):
        """Tool execution validates params correctly."""

        @register_mds_tool(
            name="executable_tool",
            params_model=MethodParams,
            description="Executable tool",
            category="test",
        )
        async def executable_tool(ctx: MDSContext, **kwargs):
            return kwargs

        tool_def = get_tool_definition("executable_tool")

        # Validate params
        params = {"title": "Test", "description": "Description", "count": 10}
        validated = tool_def.validate_params(params)

        # Execute with validated params (converted back to dict)
        ctx = MDSContext(session_id="test", user_id="test_user")
        result = await tool_def.implementation(ctx, **validated.model_dump())

        assert result["title"] == "Test"
        assert result["count"] == 10
