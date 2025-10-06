"""
YAML Configuration Validation Tests

Validates YAML structure, schema compliance, and data integrity.
Ensures methods_inventory_v1.yaml is consistent and complete.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Set
import yaml
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

METHODS_YAML_PATH = PROJECT_ROOT / "config" / "methods_inventory_v1.yaml"


class YAMLValidationReport:
    """Generates YAML validation reports."""
    
    def __init__(self):
        self.results = {
            "total_methods": 0,
            "valid_methods": 0,
            "invalid_methods": 0,
            "schema_errors": [],
            "data_errors": [],
            "missing_fields": [],
            "duplicate_names": []
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        success_rate = (self.results["valid_methods"] / self.results["total_methods"] * 100) if self.results["total_methods"] > 0 else 0
        
        return {
            "summary": {
                "total_methods": self.results["total_methods"],
                "valid": self.results["valid_methods"],
                "invalid": self.results["invalid_methods"],
                "success_rate": f"{success_rate:.2f}%"
            },
            "errors": {
                "schema_errors": self.results["schema_errors"],
                "data_errors": self.results["data_errors"],
                "missing_fields": self.results["missing_fields"],
                "duplicate_names": self.results["duplicate_names"]
            }
        }


@pytest.fixture
def yaml_report():
    """Provide YAML validation report instance."""
    return YAMLValidationReport()


class TestYAMLStructure:
    """Test suite for YAML structure validation."""
    
    def test_yaml_file_exists_and_parseable(self):
        """Verify YAML file exists and can be parsed."""
        print("\n" + "="*80)
        print("YAML FILE EXISTENCE TEST")
        print("="*80)
        
        assert METHODS_YAML_PATH.exists(), f"methods_inventory_v1.yaml not found at {METHODS_YAML_PATH}"
        print(f"  ✅ File exists: {METHODS_YAML_PATH.relative_to(PROJECT_ROOT)}")
        
        try:
            with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            assert data is not None, "YAML file is empty"
            assert isinstance(data, dict), "YAML root must be a dictionary"
            print(f"  ✅ File is parseable YAML")
            
        except yaml.YAMLError as e:
            pytest.fail(f"YAML parsing error: {e}")
    
    def test_yaml_header_structure(self):
        """Validate YAML header fields."""
        print("\n" + "="*80)
        print("YAML HEADER VALIDATION TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        required_header_fields = [
            "version",
            "schema_version",
            "description",
            "methods"
        ]
        
        errors = []
        
        for field in required_header_fields:
            if field not in data:
                errors.append(f"Missing header field: {field}")
                print(f"  ❌ Missing: {field}")
            else:
                print(f"  ✅ {field}: {data[field] if field != 'methods' else f'{len(data[field])} methods'}")
        
        assert len(errors) == 0, f"Header validation failed:\n" + "\n".join(errors)
    
    def test_all_methods_have_required_fields(self, yaml_report):
        """Verify each method has required fields."""
        print("\n" + "="*80)
        print("METHOD SCHEMA VALIDATION TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        yaml_report.results["total_methods"] = len(methods)
        
        required_fields = [
            "name",
            "description",
            "classification",
            "module_path",
            "class_name",
            "method_name",
            "business_rules",
            "models"
        ]
        
        required_classification_fields = [
            "domain",
            "subdomain",
            "capability",
            "complexity",
            "maturity",
            "integration_tier"
        ]
        
        for i, method in enumerate(methods):
            method_name = method.get("name", f"method_{i}")
            errors = []
            
            # Check top-level required fields
            for field in required_fields:
                if field not in method:
                    errors.append(f"Missing field: {field}")
            
            # Check classification fields
            if "classification" in method:
                classification = method["classification"]
                for field in required_classification_fields:
                    if field not in classification:
                        errors.append(f"Missing classification.{field}")
            
            if errors:
                yaml_report.results["invalid_methods"] += 1
                yaml_report.results["schema_errors"].append({
                    "method": method_name,
                    "errors": errors
                })
                print(f"  ❌ {method_name}")
                for error in errors:
                    print(f"     - {error}")
            else:
                yaml_report.results["valid_methods"] += 1
                print(f"  ✅ {method_name}")
        
        report = yaml_report.generate_report()
        print(f"\nResult: {report['summary']['valid']}/{report['summary']['total_methods']} methods valid")
        print(f"Success Rate: {report['summary']['success_rate']}")
        
        assert yaml_report.results["invalid_methods"] == 0, f"Found {yaml_report.results['invalid_methods']} invalid methods"
    
    def test_no_duplicate_method_names(self):
        """Verify no duplicate method names exist."""
        print("\n" + "="*80)
        print("DUPLICATE METHOD NAMES TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        method_names: Set[str] = set()
        duplicates = []
        
        for method in methods:
            name = method.get("name")
            if name:
                if name in method_names:
                    duplicates.append(name)
                    print(f"  ❌ Duplicate: {name}")
                else:
                    method_names.add(name)
        
        if not duplicates:
            print(f"  ✅ No duplicates found ({len(method_names)} unique methods)")
        
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate method names: {duplicates}"
    
    def test_classification_values_valid(self):
        """Validate classification field values against allowed values."""
        print("\n" + "="*80)
        print("CLASSIFICATION VALUES VALIDATION TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        
        allowed_values = {
            "domain": ["workspace", "communication", "automation"],
            "capability": ["create", "read", "update", "delete", "process", "search"],
            "complexity": ["atomic", "composite", "pipeline"],
            "maturity": ["experimental", "beta", "stable", "deprecated"],
            "integration_tier": ["internal", "external", "hybrid"]
        }
        
        errors = []
        
        for method in methods:
            method_name = method.get("name", "unknown")
            classification = method.get("classification", {})
            
            for field, allowed in allowed_values.items():
                value = classification.get(field)
                if value and value not in allowed:
                    error_msg = f"{method_name}: classification.{field}='{value}' not in {allowed}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
        
        if not errors:
            print(f"  ✅ All classification values valid")
        
        assert len(errors) == 0, f"Found {len(errors)} invalid classification values"
    
    def test_model_references_format(self):
        """Validate model references are properly formatted."""
        print("\n" + "="*80)
        print("MODEL REFERENCES FORMAT TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        
        errors = []
        missing_models = []
        
        for method in methods:
            method_name = method.get("name", "unknown")
            models = method.get("models", {})
            
            request_model = models.get("request_model")
            response_model = models.get("response_model")
            
            # Check if models are specified
            if not request_model:
                missing_models.append(f"{method_name}: missing request_model")
            else:
                # Validate format (should be a string)
                if not isinstance(request_model, str):
                    errors.append(f"{method_name}: request_model must be a string")
                print(f"  ✅ {method_name}: {request_model} / {response_model}")
            
            if not response_model:
                missing_models.append(f"{method_name}: missing response_model")
            else:
                if not isinstance(response_model, str):
                    errors.append(f"{method_name}: response_model must be a string")
        
        print(f"\n📊 Model Coverage:")
        print(f"  - Methods with models: {len(methods) - len(missing_models)}/{len(methods)}")
        print(f"  - Missing models: {len(missing_models)}")
        
        if missing_models:
            print(f"\n⚠️  Missing Models:")
            for missing in missing_models[:5]:  # Show first 5
                print(f"  - {missing}")
            if len(missing_models) > 5:
                print(f"  ... and {len(missing_models) - 5} more")
        
        assert len(errors) == 0, f"Found {len(errors)} model format errors"


class TestYAMLDataIntegrity:
    """Test data integrity and relationships in YAML."""
    
    def test_method_naming_convention(self):
        """Verify method names follow naming convention."""
        print("\n" + "="*80)
        print("METHOD NAMING CONVENTION TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        
        # Expected pattern: {domain}.{subdomain}.{capability}_{name}
        errors = []
        passed = 0
        
        for method in methods:
            method_name = method.get("name", "")
            classification = method.get("classification", {})
            
            domain = classification.get("domain", "")
            subdomain = classification.get("subdomain", "")
            
            # Check if name starts with domain.subdomain
            expected_prefix = f"{domain}.{subdomain}."
            
            if method_name.startswith(expected_prefix):
                print(f"  ✅ {method_name}")
                passed += 1
            else:
                errors.append(f"{method_name} should start with '{expected_prefix}'")
                print(f"  ⚠️  {method_name} (expected prefix: {expected_prefix})")
        
        print(f"\nResult: {passed}/{len(methods)} methods follow convention")
        
        # This is a warning, not a hard failure
        if errors:
            print(f"\n⚠️  Naming convention warnings (not critical):")
            for error in errors[:5]:
                print(f"  - {error}")
    
    def test_business_rules_completeness(self):
        """Verify business_rules section is complete."""
        print("\n" + "="*80)
        print("BUSINESS RULES COMPLETENESS TEST")
        print("="*80)
        
        with open(METHODS_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        methods = data.get("methods", [])
        
        required_business_rule_fields = [
            "required_permissions",
            "resource_type",
            "idempotent",
            "transactional"
        ]
        
        errors = []
        passed = 0
        
        for method in methods:
            method_name = method.get("name", "unknown")
            business_rules = method.get("business_rules", {})
            
            missing = []
            for field in required_business_rule_fields:
                if field not in business_rules:
                    missing.append(field)
            
            if missing:
                errors.append(f"{method_name}: missing {', '.join(missing)}")
                print(f"  ❌ {method_name}: missing {', '.join(missing)}")
            else:
                passed += 1
                print(f"  ✅ {method_name}")
        
        print(f"\nResult: {passed}/{len(methods)} methods have complete business rules")
        
        assert len(errors) == 0, f"Found {len(errors)} methods with incomplete business rules"


if __name__ == "__main__":
    # Run with: python -m pytest tests/system_validation/test_yaml_validation.py -v -s
    pytest.main([__file__, "-v", "-s"])
