"""
Test ToolFactory integration with MANAGED_METHODS registry.

Validates:
1. ToolFactory detects api_call method_name in MANAGED_METHODS
2. Enriches config with method metadata
3. Validation fails if method not found
4. Auto-generates request_mapping from method parameters
"""

import sys
from pathlib import Path
import tempfile
import yaml

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pydantic import BaseModel, Field
from pydantic_ai_integration.method_decorator import register_service_method
from pydantic_ai_integration.method_registry import register_method, get_method_definition
from pydantic_ai_integration.tools.factory import ToolFactory
from pydantic_models.base.envelopes import BaseRequest, BaseResponse


# Test models
class TestPayload(BaseModel):
    """Test payload."""
    value: int = Field(..., description="Test value")
    name: str = Field(..., description="Test name")


class TestRequest(BaseRequest[TestPayload]):
    """Test request."""
    pass


class TestResponse(BaseResponse[dict]):
    """Test response."""
    pass


# Register a test method
@register_service_method(
    name="test_api_method",
    description="Test method for ToolFactory integration",
    service_name="TestService",
    service_module="tests.test_factory_integration",
    classification={
        "domain": "workspace",
        "subdomain": "test",
        "capability": "create",
        "complexity": "atomic",
        "maturity": "experimental",
        "integration_tier": "internal"
    },
    required_permissions=["test:execute"],
    requires_casefile=False,
    enabled=True
)
async def test_api_method(self, request: TestRequest) -> TestResponse:
    """Test method implementation."""
    return TestResponse(
        request_id=request.request_id,
        status="completed",
        payload={"result": request.payload.value * 2}
    )


def test_factory_detects_registered_method():
    """Test that ToolFactory detects method in MANAGED_METHODS."""
    print("[TEST] Testing ToolFactory method detection...")
    
    # Create temporary YAML with api_call pointing to registered method
    yaml_content = """
name: test_tool_with_api_call
description: "Test tool using api_call"
category: test

business_rules:
  requires_auth: true
  required_permissions:
    - test:execute

parameters:
  - name: value
    type: integer
    required: true
    description: "Test value"
  - name: name
    type: string
    required: true
    description: "Test name"

implementation:
  type: api_call
  api_call:
    client_module: "tests.test_factory_integration"
    client_class: "TestService"
    method_name: "test_api_method"
    request_type: "TestRequest"
    response_type: "TestResponse"

returns:
  type: object
  description: "Result payload"
  properties:
    result:
      type: integer
      description: "Doubled value"

examples:
  - description: "Basic example"
    input:
      value: 42
      name: "test"
    expected_output:
      result: 84
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create config structure
        config_dir = tmpdir_path / "config" / "tools"
        config_dir.mkdir(parents=True)
        
        yaml_file = config_dir / "test_tool_with_api_call.yaml"
        yaml_file.write_text(yaml_content)
        
        # Create factory
        factory = ToolFactory(project_root=tmpdir_path)
        
        # Load config
        config = factory.load_tool_config(yaml_file)
        
        # Check that method was detected
        api_call = config["implementation"]["api_call"]
        assert "_method_metadata" in api_call, "Method metadata not enriched!"
        
        metadata = api_call["_method_metadata"]
        assert metadata["service_name"] == "TestService"
        assert metadata["request_model"] == "TestRequest"
        assert metadata["response_model"] == "TestResponse"
        assert "test:execute" in metadata["required_permissions"]
        
        print("  [OK] ToolFactory detected method in MANAGED_METHODS")
        print(f"    - Service: {metadata['service_name']}")
        print(f"    - Request: {metadata['request_model']}")
        print(f"    - Response: {metadata['response_model']}")


def test_factory_validation_fails_for_missing_method():
    """Test that validation fails if method not in MANAGED_METHODS."""
    print("[TEST] Testing validation for missing method...")
    
    yaml_content = """
name: test_tool_missing_method
description: "Test tool with missing method"
category: test

business_rules:
  requires_auth: true

parameters:
  - name: value
    type: integer
    required: true

implementation:
  type: api_call
  api_call:
    client_module: "some.module"
    client_class: "SomeClass"
    method_name: "nonexistent_method"
    request_type: "SomeRequest"
    response_type: "SomeResponse"

returns:
  type: object
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        config_dir = tmpdir_path / "config" / "tools"
        config_dir.mkdir(parents=True)
        
        yaml_file = config_dir / "test_tool_missing_method.yaml"
        yaml_file.write_text(yaml_content)
        
        factory = ToolFactory(project_root=tmpdir_path)
        
        # Load config
        config = factory.load_tool_config(yaml_file)
        
        # Validate - should have issues
        issues = factory.validate_config(config)
        
        assert len(issues) > 0, "Expected validation errors!"
        assert any("nonexistent_method" in issue for issue in issues), \
            "Expected error about missing method!"
        
        print("  [OK] Validation correctly failed for missing method")
        print(f"    - Error: {issues[0]}")


def test_factory_works_with_registered_method():
    """Test that ToolFactory successfully validates tool with registered method."""
    print("[TEST] Testing full validation with registered method...")
    
    yaml_content = """
name: test_validated_tool
description: "Test tool with validated method"
category: test

business_rules:
  requires_auth: true
  required_permissions:
    - test:execute

parameters:
  - name: value
    type: integer
    required: true
    description: "Test value"
  - name: name
    type: string
    required: true
    description: "Test name"

implementation:
  type: api_call
  api_call:
    client_module: "tests.test_factory_integration"
    client_class: "TestService"
    method_name: "test_api_method"
    request_type: "TestRequest"
    response_type: "TestResponse"

returns:
  type: object

examples:
  - description: "Valid example"
    input:
      value: 10
      name: "test"
    expected_output:
      result: 20
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        config_dir = tmpdir_path / "config" / "tools"
        config_dir.mkdir(parents=True)
        
        yaml_file = config_dir / "test_validated_tool.yaml"
        yaml_file.write_text(yaml_content)
        
        factory = ToolFactory(project_root=tmpdir_path)
        
        # Load and validate
        config = factory.load_tool_config(yaml_file)
        issues = factory.validate_config(config)
        
        assert len(issues) == 0, f"Unexpected validation errors: {issues}"
        
        print("  [OK] Validation passed for tool with registered method")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("TOOLFACTORY <-> MANAGED_METHODS INTEGRATION TESTS")
    print("="*60 + "\n")
    
    try:
        test_factory_detects_registered_method()
        test_factory_validation_fails_for_missing_method()
        test_factory_works_with_registered_method()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
