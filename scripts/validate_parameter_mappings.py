"""
Parameter mapping validation script.

Validates tool-to-method parameter mappings and generates a report.
Run this script to check for parameter mismatches in the registry.

Usage:
    python scripts/validate_parameter_mappings.py [--verbose] [--errors-only]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from pydantic_ai_integration.registry import validate_parameter_mappings


def main():
    """Run parameter mapping validation."""
    parser = argparse.ArgumentParser(
        description="Validate tool-to-method parameter mappings"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for all checks"
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only show tools with errors (hide warnings)"
    )
    parser.add_argument(
        "--include-no-method",
        action="store_true",
        help="Include tools without method references in validation"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("PARAMETER MAPPING VALIDATION")
    print("=" * 70)
    print()
    
    # Load tools from YAML before validation
    print("Loading tools from YAML...")
    try:
        # Set environment variable to skip auto-initialization
        import os
        os.environ["SKIP_AUTO_INIT"] = "true"
        
        # Add src to path for imports
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        src_path = str(project_root / "src")
        sys.path.insert(0, src_path)
        print(f"Added {src_path} to sys.path")
        print(f"sys.path[0]: {sys.path[0]}")
        
        # Load methods from YAML instead of importing service modules
        print("Loading methods from YAML...")
        from pydantic_ai_integration.method_decorator import register_methods_from_yaml
        try:
            register_methods_from_yaml("config/methods_inventory_v1.yaml")
            print("✓ Methods loaded from YAML")
        except Exception as e:
            print(f"❌ Failed to load methods from YAML: {e}")
        
        # Check if methods are loaded
        from pydantic_ai_integration.method_registry import MANAGED_METHODS
        print(f"✓ MANAGED_METHODS populated with {len(MANAGED_METHODS)} methods")
        
        from pydantic_ai_integration.tool_decorator import register_tools_from_yaml
        register_tools_from_yaml()
        print("✓ Tools loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load tools: {e}")
        return 1
    print()
    
    # Run validation
    report = validate_parameter_mappings(
        skip_tools_without_methods=not args.include_no_method
    )
    
    # Print summary
    print(f"Tools Checked: {report.tools_checked}/{report.total_tools}")
    print(f"Tools with Issues: {report.tools_with_mismatches}")
    print(f"Total Mismatches: {report.total_mismatches}")
    print(f"  - Errors: {report.error_count}")
    print(f"  - Warnings: {report.warning_count}")
    print()
    
    if report.tools_without_methods and args.verbose:
        print(f"Tools without method reference: {len(report.tools_without_methods)}")
        for tool_name in report.tools_without_methods:
            print(f"  - {tool_name}")
        print()
    
    # Print mismatches
    if report.mismatches:
        print("=" * 70)
        print("MISMATCHES")
        print("=" * 70)
        print()
        
        current_tool = None
        for mismatch in sorted(report.mismatches, key=lambda m: (m.tool_name, m.parameter_name)):
            # Skip warnings if errors-only mode
            if args.errors_only and mismatch.severity != "error":
                continue
            
            # Print tool header
            if mismatch.tool_name != current_tool:
                current_tool = mismatch.tool_name
                print(f"\n{current_tool} -> {mismatch.method_name}")
                print("-" * 70)
            
            # Print mismatch
            severity_icon = "[ERROR]" if mismatch.severity == "error" else "[WARN]" if mismatch.severity == "warning" else "[INFO]"
            print(f"  {severity_icon} {mismatch.parameter_name}: {mismatch.message}")
            
            if args.verbose and (mismatch.tool_value or mismatch.method_value):
                if mismatch.tool_value:
                    print(f"      Tool value: {mismatch.tool_value}")
                if mismatch.method_value:
                    print(f"      Method value: {mismatch.method_value}")
    else:
        print("[OK] No parameter mismatches found!")
        print()
    
    # Exit with appropriate code
    if report.has_errors:
        print()
        print("=" * 70)
        print(f"[FAILED] VALIDATION FAILED - {report.error_count} errors found")
        print("=" * 70)
        sys.exit(1)
    elif report.warning_count > 0:
        print()
        print("=" * 70)
        print(f"[WARN] VALIDATION PASSED WITH WARNINGS - {report.warning_count} warnings")
        print("=" * 70)
        sys.exit(0)
    else:
        print()
        print("=" * 70)
        print("[OK] VALIDATION PASSED - All parameter mappings valid")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
