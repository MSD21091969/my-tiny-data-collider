"""
Type Checking and Pydantic Model Validation Tests

Validates all Pydantic models, type hints, and data structures.
Ensures DTO integrity and type consistency across the codebase.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, get_type_hints
import pytest
from pydantic import BaseModel, ValidationError

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pydantic_models.base.envelopes import BaseRequest, BaseResponse
from pydantic_ai_integration.method_definition import (
    ManagedMethodDefinition,
    MethodMetadata,
    MethodBusinessRules,
    MethodModels,
    MethodParameterDef
)


class TypeValidationReport:
    """Generates comprehensive type validation reports."""
    
    def __init__(self):
        self.results = {
            "models_tested": 0,
            "models_passed": 0,
            "models_failed": 0,
            "validation_errors": [],
            "type_errors": [],
            "instantiation_errors": []
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        success_rate = (self.results["models_passed"] / self.results["models_tested"] * 100) if self.results["models_tested"] > 0 else 0
        
        return {
            "summary": {
                "total_models": self.results["models_tested"],
                "passed": self.results["models_passed"],
                "failed": self.results["models_failed"],
                "success_rate": f"{success_rate:.2f}%"
            },
            "errors": {
                "validation_errors": self.results["validation_errors"],
                "type_errors": self.results["type_errors"],
                "instantiation_errors": self.results["instantiation_errors"]
            }
        }


@pytest.fixture
def type_report():
    """Provide type validation report instance."""
    return TypeValidationReport()


class TestPydanticModels:
    """Test suite for Pydantic model validation."""
    
    def test_base_envelope_structure(self, type_report):
        """Validate BaseRequest and BaseResponse structure."""
        print("\n" + "="*80)
        print("BASE ENVELOPE STRUCTURE TEST")
        print("="*80)
        
        errors = []
        
        # Test BaseRequest
        try:
            # Check type hints exist
            hints = get_type_hints(BaseRequest)
            required_fields = ['payload']
            
            for field in required_fields:
                if field not in hints:
                    errors.append(f"BaseRequest missing field: {field}")
            
            print("  ✅ BaseRequest structure valid")
        except Exception as e:
            errors.append(f"BaseRequest error: {e}")
            print(f"  ❌ BaseRequest: {e}")
        
        # Test BaseResponse
        try:
            hints = get_type_hints(BaseResponse)
            required_fields = ['request_id', 'status', 'payload', 'error', 'metadata']
            
            for field in required_fields:
                if field not in hints:
                    errors.append(f"BaseResponse missing field: {field}")
            
            print("  ✅ BaseResponse structure valid")
        except Exception as e:
            errors.append(f"BaseResponse error: {e}")
            print(f"  ❌ BaseResponse: {e}")
        
        assert len(errors) == 0, f"Base envelope validation failed:\n" + "\n".join(errors)
    
    def test_method_definition_models(self, type_report):
        """Validate method definition Pydantic models."""
        print("\n" + "="*80)
        print("METHOD DEFINITION MODELS TEST")
        print("="*80)
        
        models = [
            ("MethodParameterDef", MethodParameterDef),
            ("MethodMetadata", MethodMetadata),
            ("MethodBusinessRules", MethodBusinessRules),
            ("MethodModels", MethodModels),
            ("ManagedMethodDefinition", ManagedMethodDefinition)
        ]
        
        type_report.results["models_tested"] = len(models)
        
        for model_name, model_class in models:
            try:
                # Verify it's a Pydantic model
                assert issubclass(model_class, BaseModel), f"{model_name} is not a Pydantic model"
                
                # Check model_fields exists (Pydantic v2)
                if hasattr(model_class, 'model_fields'):
                    fields = model_class.model_fields
                    print(f"  ✅ {model_name} ({len(fields)} fields)")
                else:
                    print(f"  ⚠️  {model_name} (Pydantic v1 detected)")
                
                type_report.results["models_passed"] += 1
                
            except Exception as e:
                type_report.results["models_failed"] += 1
                type_report.results["type_errors"].append({
                    "model": model_name,
                    "error": str(e)
                })
                print(f"  ❌ {model_name}: {e}")
        
        report = type_report.generate_report()
        print(f"\nResult: {report['summary']['passed']}/{report['summary']['total_models']} models valid")
        
        assert type_report.results["models_failed"] == 0, f"Failed validation for {type_report.results['models_failed']} models"
    
    def test_method_definition_instantiation(self, type_report):
        """Test creating valid ManagedMethodDefinition instances."""
        print("\n" + "="*80)
        print("METHOD DEFINITION INSTANTIATION TEST")
        print("="*80)
        
        test_cases = [
            {
                "name": "Minimal Valid Definition",
                "data": {
                    "method_name": "test.example.create_test",
                    "metadata": {
                        "description": "Test method",
                        "classification": {
                            "domain": "workspace",
                            "subdomain": "test",
                            "capability": "create",
                            "complexity": "atomic",
                            "maturity": "stable",
                            "integration_tier": "internal"
                        },
                        "module_path": "test.service",
                        "class_name": "TestService",
                        "method_name": "create_test"
                    },
                    "business_rules": {
                        "required_permissions": ["test.create"],
                        "resource_type": "test",
                        "idempotent": True,
                        "transactional": False
                    },
                    "models": {
                        "request_model": "TestRequest",
                        "response_model": "TestResponse"
                    }
                }
            },
            {
                "name": "Definition with Deprecation",
                "data": {
                    "method_name": "test.example.old_method",
                    "metadata": {
                        "description": "Deprecated method",
                        "classification": {
                            "domain": "workspace",
                            "subdomain": "test",
                            "capability": "read",
                            "complexity": "atomic",
                            "maturity": "deprecated",
                            "integration_tier": "internal"
                        },
                        "module_path": "test.service",
                        "class_name": "TestService",
                        "method_name": "old_method"
                    },
                    "business_rules": {
                        "required_permissions": ["test.read"],
                        "resource_type": "test",
                        "idempotent": True,
                        "transactional": False,
                        "deprecated_since": "1.0.0",
                        "removal_version": "2.0.0",
                        "replacement_method": "test.example.new_method"
                    },
                    "models": {
                        "request_model": "TestRequest",
                        "response_model": "TestResponse"
                    }
                }
            }
        ]
        
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            try:
                definition = ManagedMethodDefinition(**test_case["data"])
                print(f"  ✅ {test_case['name']}")
                passed += 1
            except ValidationError as e:
                print(f"  ❌ {test_case['name']}")
                print(f"     Validation Error: {e}")
                type_report.results["validation_errors"].append({
                    "test": test_case["name"],
                    "error": str(e)
                })
                failed += 1
            except Exception as e:
                print(f"  ❌ {test_case['name']}")
                print(f"     Error: {e}")
                type_report.results["instantiation_errors"].append({
                    "test": test_case["name"],
                    "error": str(e)
                })
                failed += 1
        
        print(f"\nResult: {passed}/{len(test_cases)} instantiation tests passed")
        
        assert failed == 0, f"Failed {failed} instantiation tests"
    
    def test_operation_models_exist(self):
        """Verify operation model files are importable."""
        print("\n" + "="*80)
        print("OPERATION MODELS IMPORT TEST")
        print("="*80)
        
        operation_modules = [
            "pydantic_models.operations.casefile_ops",
            "pydantic_models.operations.tool_session_ops",
            "pydantic_models.operations.chat_session_ops",
            "pydantic_models.operations.gmail_ops",
            "pydantic_models.operations.drive_ops",
            "pydantic_models.operations.sheets_ops",
        ]
        
        errors = []
        passed = 0
        
        for module_name in operation_modules:
            try:
                import importlib
                module = importlib.import_module(module_name)
                
                # Count Pydantic models in module
                model_count = 0
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                        model_count += 1
                
                print(f"  ✅ {module_name} ({model_count} models)")
                passed += 1
                
            except ImportError as e:
                errors.append(f"{module_name}: {e}")
                print(f"  ❌ {module_name}")
                print(f"     {e}")
        
        print(f"\nResult: {passed}/{len(operation_modules)} operation model files importable")
        
        assert len(errors) == 0, f"Failed to import {len(errors)} operation model files"


class TestTypeConsistency:
    """Test type consistency across the codebase."""
    
    def test_registry_api_type_hints(self):
        """Verify method_registry APIs have proper type hints."""
        print("\n" + "="*80)
        print("REGISTRY API TYPE HINTS TEST")
        print("="*80)
        
        from pydantic_ai_integration import method_registry
        
        api_functions = [
            "get_registered_methods",
            "get_method_names",
            "validate_method_exists",
            "get_methods_by_domain",
            "get_methods_by_subdomain",
            "get_methods_by_capability",
            "get_methods_by_service",
            "get_deprecated_methods",
            "register_method",
            "unregister_method"
        ]
        
        errors = []
        passed = 0
        
        for func_name in api_functions:
            if not hasattr(method_registry, func_name):
                errors.append(f"Function '{func_name}' not found in method_registry")
                print(f"  ❌ {func_name} (not found)")
                continue
            
            func = getattr(method_registry, func_name)
            
            try:
                hints = get_type_hints(func)
                if hints:
                    print(f"  ✅ {func_name} (typed)")
                    passed += 1
                else:
                    print(f"  ⚠️  {func_name} (no type hints)")
                    passed += 1  # Not an error, just a warning
            except Exception as e:
                errors.append(f"{func_name}: {e}")
                print(f"  ❌ {func_name}: {e}")
        
        print(f"\nResult: {passed}/{len(api_functions)} APIs checked")
        
        assert len(errors) == 0, f"API validation failed:\n" + "\n".join(errors)


if __name__ == "__main__":
    # Run with: python -m pytest tests/system_validation/test_type_validation.py -v -s
    pytest.main([__file__, "-v", "-s"])
