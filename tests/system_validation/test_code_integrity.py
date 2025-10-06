"""
System-Wide Code Integrity Tests

Validates fundamental code structure, imports, and syntax across the entire codebase.
Catches refactoring issues, broken imports, and structural problems.
"""

import ast
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


class CodeIntegrityValidator:
    """Validates code integrity across the project."""
    
    def __init__(self):
        self.results = {
            "syntax_errors": [],
            "import_errors": [],
            "missing_files": [],
            "circular_imports": [],
            "total_files_checked": 0,
            "passed": 0,
            "failed": 0
        }
    
    def validate_python_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Check if Python file has valid syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, "OK"
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def validate_imports(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check if all imports in a file are valid."""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            importlib.import_module(alias.name)
                        except ImportError as e:
                            errors.append(f"Import '{alias.name}': {e}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            importlib.import_module(node.module)
                        except ImportError as e:
                            errors.append(f"From '{node.module}': {e}")
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [str(e)]
    
    def scan_directory(self, directory: Path, pattern: str = "*.py") -> List[Path]:
        """Recursively scan directory for Python files."""
        return list(directory.rglob(pattern))
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        success_rate = (self.results["passed"] / self.results["total_files_checked"] * 100) if self.results["total_files_checked"] > 0 else 0
        
        return {
            "summary": {
                "total_files": self.results["total_files_checked"],
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "success_rate": f"{success_rate:.2f}%"
            },
            "details": {
                "syntax_errors": self.results["syntax_errors"],
                "import_errors": self.results["import_errors"],
                "missing_files": self.results["missing_files"],
                "circular_imports": self.results["circular_imports"]
            }
        }


@pytest.fixture
def validator():
    """Provide validator instance."""
    return CodeIntegrityValidator()


class TestCodeIntegrity:
    """Test suite for code integrity validation."""
    
    def test_all_python_files_valid_syntax(self, validator):
        """Validate syntax of all Python files in src/."""
        src_dir = PROJECT_ROOT / "src"
        python_files = validator.scan_directory(src_dir)
        
        validator.results["total_files_checked"] = len(python_files)
        
        for file_path in python_files:
            is_valid, error_msg = validator.validate_python_syntax(file_path)
            
            if is_valid:
                validator.results["passed"] += 1
            else:
                validator.results["failed"] += 1
                validator.results["syntax_errors"].append({
                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                    "error": error_msg
                })
        
        report = validator.generate_report()
        print("\n" + "="*80)
        print("CODE INTEGRITY REPORT - Syntax Validation")
        print("="*80)
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['success_rate']}")
        
        if report['details']['syntax_errors']:
            print("\nSYNTAX ERRORS:")
            for error in report['details']['syntax_errors']:
                print(f"  ❌ {error['file']}")
                print(f"     {error['error']}")
        
        assert len(report['details']['syntax_errors']) == 0, f"Found {len(report['details']['syntax_errors'])} syntax errors"
    
    def test_critical_modules_importable(self):
        """Verify critical modules can be imported."""
        critical_modules = [
            "pydantic_ai_integration.method_definition",
            "pydantic_ai_integration.method_registry",
            "pydantic_ai_integration.method_decorator",
            "pydantic_models.base.envelopes",
            "pydantic_models.operations.casefile_ops",
            "pydantic_models.operations.tool_session_ops",
        ]
        
        errors = []
        passed = 0
        
        print("\n" + "="*80)
        print("CRITICAL MODULE IMPORT TEST")
        print("="*80)
        
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                print(f"  ✅ {module_name}")
                passed += 1
            except ImportError as e:
                error_msg = f"{module_name}: {e}"
                errors.append(error_msg)
                print(f"  ❌ {module_name}")
                print(f"     {e}")
        
        print(f"\nResult: {passed}/{len(critical_modules)} modules importable")
        
        assert len(errors) == 0, f"Failed to import {len(errors)} critical modules:\n" + "\n".join(errors)
    
    def test_service_classes_exist(self):
        """Verify all service classes are accessible."""
        services = [
            ("casefileservice.service", "CasefileService"),
            ("gmailclient.service", "GmailClient"),
            ("driveclient.service", "DriveClient"),
            ("sheetsclient.service", "SheetsClient"),
            ("communicationservice.service", "CommunicationService"),
            ("pydantic_ai_integration.tool_session_service", "ToolSessionService"),
        ]
        
        errors = []
        passed = 0
        
        print("\n" + "="*80)
        print("SERVICE CLASS AVAILABILITY TEST")
        print("="*80)
        
        for module_name, class_name in services:
            try:
                module = importlib.import_module(module_name)
                if not hasattr(module, class_name):
                    error_msg = f"{module_name}.{class_name} not found"
                    errors.append(error_msg)
                    print(f"  ❌ {class_name}")
                else:
                    print(f"  ✅ {class_name}")
                    passed += 1
            except ImportError as e:
                error_msg = f"{module_name}: {e}"
                errors.append(error_msg)
                print(f"  ❌ {class_name} (module import failed)")
        
        print(f"\nResult: {passed}/{len(services)} services accessible")
        
        assert len(errors) == 0, f"Failed to access {len(errors)} services:\n" + "\n".join(errors)


if __name__ == "__main__":
    # Run with: python -m pytest tests/system_validation/test_code_integrity.py -v
    pytest.main([__file__, "-v", "-s"])
