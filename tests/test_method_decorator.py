"""
Test the @register_service_method decorator.

Validates:
1. Decorator registers methods in MANAGED_METHODS
2. Metadata is correctly extracted
3. Classification is properly stored
4. Discovery APIs work correctly
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pydantic import BaseModel, Field
from pydantic_ai_integration.method_decorator import register_service_method
from pydantic_ai_integration.method_registry import (
    get_registered_methods,
    get_method_names,
    get_methods_by_domain,
    get_methods_by_capability,
    validate_method_exists
)
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


# Test service method with decorator
@register_service_method(
    name="test_method",
    description="Test method for validation",
    service_name="TestService",
    service_module="tests.test_method_decorator",
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
async def test_method(self, request: TestRequest) -> TestResponse:
    """Test method implementation."""
    return TestResponse(
        request_id=request.request_id,
        status="completed",
        payload={"result": request.payload.value * 2}
    )


def test_decorator_registers_method():
    """Test that decorator registers method in MANAGED_METHODS."""
    print("✓ Testing method registration...")
    
    # Check method is registered
    assert validate_method_exists("test_method"), "Method not registered!"
    
    # Check method appears in names
    method_names = get_method_names()
    assert "test_method" in method_names, "Method not in names list!"
    
    print("  ✓ Method registered successfully")


def test_metadata_extraction():
    """Test that metadata is correctly extracted."""
    print("✓ Testing metadata extraction...")
    
    methods = get_registered_methods()
    method_def = methods.get("test_method")
    
    assert method_def is not None, "Method definition not found!"
    
    # Check metadata
    assert method_def.metadata.name == "test_method"
    assert method_def.metadata.service_name == "TestService"
    assert method_def.metadata.description == "Test method for validation"
    
    # Check classification
    assert method_def.metadata.domain == "workspace"
    assert method_def.metadata.subdomain == "test"
    assert method_def.metadata.capability == "create"
    assert method_def.metadata.complexity == "atomic"
    assert method_def.metadata.maturity == "experimental"
    assert method_def.metadata.integration_tier == "internal"
    
    print("  ✓ Metadata extracted correctly")


def test_business_rules():
    """Test that business rules are correctly stored."""
    print("✓ Testing business rules...")
    
    methods = get_registered_methods()
    method_def = methods.get("test_method")
    
    assert method_def.business_rules.enabled == True
    assert method_def.business_rules.requires_auth == True
    assert "test:execute" in method_def.business_rules.required_permissions
    assert method_def.business_rules.requires_casefile == False
    
    print("  ✓ Business rules stored correctly")


def test_model_references():
    """Test that model references are correctly stored."""
    print("✓ Testing model references...")
    
    methods = get_registered_methods()
    method_def = methods.get("test_method")
    
    assert method_def.models.request_model_name == "TestRequest"
    assert method_def.models.response_model_name == "TestResponse"
    
    print("  ✓ Model references stored correctly")


def test_discovery_apis():
    """Test that discovery APIs work correctly."""
    print("✓ Testing discovery APIs...")
    
    # Test by domain
    workspace_methods = get_methods_by_domain("workspace")
    assert len(workspace_methods) > 0, "No workspace methods found!"
    assert any(m.metadata.name == "test_method" for m in workspace_methods)
    
    # Test by capability
    create_methods = get_methods_by_capability("create")
    assert len(create_methods) > 0, "No create methods found!"
    assert any(m.metadata.name == "test_method" for m in create_methods)
    
    print("  ✓ Discovery APIs working correctly")


def test_parameter_extraction():
    """Test that parameters are extracted from request model."""
    print("✓ Testing parameter extraction...")
    
    methods = get_registered_methods()
    method_def = methods.get("test_method")
    
    # Should have extracted parameters from TestPayload
    assert len(method_def.parameters) > 0, "No parameters extracted!"
    
    param_names = [p.name for p in method_def.parameters]
    assert "value" in param_names, "value parameter not extracted!"
    assert "name" in param_names, "name parameter not extracted!"
    
    # Check parameter details
    value_param = next(p for p in method_def.parameters if p.name == "value")
    assert value_param.required == True
    assert value_param.description == "Test value"
    
    print("  ✓ Parameters extracted correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("METHOD DECORATOR TESTS")
    print("="*60 + "\n")
    
    try:
        test_decorator_registers_method()
        test_metadata_extraction()
        test_business_rules()
        test_model_references()
        test_discovery_apis()
        test_parameter_extraction()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
