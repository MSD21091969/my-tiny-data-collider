#!/usr/bin/env python
"""
Registry Validation Script for CI/CD.

Validates method and tool registries with comprehensive reporting.
Suitable for use in GitHub Actions, pre-commit hooks, and local validation.

Exit Codes:
    0: All validations passed
    1: Validation errors found (in STRICT mode)
    2: Script execution error

Environment Variables:
    REGISTRY_STRICT_VALIDATION: Set to 'true' for STRICT mode (default: 'true')
    SKIP_DRIFT_DETECTION: Set to 'true' to skip drift detection (default: 'false')

Usage:
    # Run with default settings (STRICT mode, drift detection enabled)
    python scripts/validate_registries.py

    # Run in WARNING mode
    REGISTRY_STRICT_VALIDATION=false python scripts/validate_registries.py

    # Skip drift detection
    SKIP_DRIFT_DETECTION=true python scripts/validate_registries.py

    # For CI/CD (use STRICT mode)
    python scripts/validate_registries.py --strict

    # Show help
    python scripts/validate_registries.py --help
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pydantic_ai_integration.registry import RegistryLoader, ValidationMode
from src.pydantic_ai_integration.registry.parameter_mapping import validate_parameter_mappings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate method and tool registries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_registries.py
  python scripts/validate_registries.py --strict
  python scripts/validate_registries.py --warning --no-drift
  python scripts/validate_registries.py --verbose
        """,
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use STRICT validation mode (fail on errors)",
    )

    parser.add_argument(
        "--warning",
        action="store_true",
        help="Use WARNING validation mode (log errors but don't fail)",
    )

    parser.add_argument(
        "--no-drift",
        action="store_true",
        help="Disable drift detection",
    )

    parser.add_argument(
        "--no-param-mapping",
        action="store_true",
        help="Disable parameter mapping validation",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output (errors only)",
    )

    return parser.parse_args()


def configure_logging(verbose: bool, quiet: bool):
    """Configure logging level based on arguments."""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)


def determine_validation_mode(args) -> ValidationMode:
    """
    Determine validation mode from arguments and environment.

    Priority:
    1. Command-line arguments (--strict or --warning)
    2. Environment variable (REGISTRY_STRICT_VALIDATION)
    3. Default (STRICT for CI/CD safety)
    """
    if args.strict:
        return ValidationMode.STRICT
    elif args.warning:
        return ValidationMode.WARNING
    else:
        # Check environment, default to STRICT
        env_mode = os.getenv("REGISTRY_STRICT_VALIDATION", "true").lower()
        return ValidationMode.STRICT if env_mode == "true" else ValidationMode.WARNING


def determine_drift_detection(args) -> bool:
    """
    Determine if drift detection should be enabled.

    Priority:
    1. Command-line argument (--no-drift)
    2. Environment variable (SKIP_DRIFT_DETECTION)
    3. Default (enabled)
    """
    if args.no_drift:
        return False

    skip_drift = os.getenv("SKIP_DRIFT_DETECTION", "false").lower()
    return skip_drift != "true"


def determine_param_mapping_validation(args) -> bool:
    """
    Determine if parameter mapping validation should be enabled.

    Priority:
    1. Command-line argument (--no-param-mapping)
    2. Environment variable (SKIP_PARAM_MAPPING)
    3. Default (enabled)
    """
    if args.no_param_mapping:
        return False

    skip_param = os.getenv("SKIP_PARAM_MAPPING", "false").lower()
    return skip_param != "true"


def print_summary(result, param_mapping_report=None):
    """Print validation summary."""
    print("\n" + "=" * 70)
    print("REGISTRY VALIDATION SUMMARY")
    print("=" * 70)

    if result.success:
        print("[OK] Status: SUCCESS")
        print(f"📊 Methods: {result.methods_count}")
        print(f"🔧 Tools: {result.tools_count}")
    else:
        print("[FAIL] Status: FAILED")
        if result.error:
            print(f"💥 Error: {result.error}")

    # Coverage report
    if result.coverage_report:
        print("\n📋 Coverage Validation:")
        if result.coverage_report.has_errors:
            print(f"  [ERROR] {result.coverage_report.error_count} issues found")
            if result.coverage_report.missing_tools:
                print(f"  - Missing tools: {len(result.coverage_report.missing_tools)}")
            if result.coverage_report.orphaned_tools:
                print(f"  - Orphaned tools: {len(result.coverage_report.orphaned_tools)}")
        else:
            print("  [OK] All checks passed")

    # Consistency report
    if result.consistency_report:
        print("\nConsistency Validation:")
        if result.consistency_report.has_errors:
            print(f"  [ERROR] {result.consistency_report.error_count} issues found")
        else:
            print("  [OK] All checks passed")

    # Drift report
    if result.drift_report:
        print("\nDrift Detection:")
        if result.drift_report.has_errors:
            print(f"  [ERROR] {result.drift_report.error_count} issues found")
            if result.drift_report.missing_in_yaml:
                print(f"  - Missing in YAML: {len(result.drift_report.missing_in_yaml)}")
            if result.drift_report.missing_in_code:
                print(f"  - Missing in code: {len(result.drift_report.missing_in_code)}")
        else:
            print("  [OK] No drift detected")

    # Parameter mapping report
    if param_mapping_report:
        print("\nParameter Mapping Validation:")
        if param_mapping_report.has_errors:
            print(f"  [ERROR] {param_mapping_report.error_count} errors, {param_mapping_report.warning_count} warnings")
            print(f"  - Tools checked: {param_mapping_report.tools_checked}/{param_mapping_report.total_tools}")
            print(f"  - Tools with issues: {param_mapping_report.tools_with_mismatches}")
        else:
            print(f"  [OK] All parameter mappings valid ({param_mapping_report.tools_checked} tools checked)")

    print("=" * 70)


def print_detailed_errors(result, param_mapping_report=None):
    """Print detailed error information."""
    has_errors = False

    # Coverage errors
    if result.coverage_report and result.coverage_report.has_errors:
        has_errors = True
        print("\n[ERROR] COVERAGE ERRORS:")
        print(result.coverage_report)

    # Consistency errors
    if result.consistency_report and result.consistency_report.has_errors:
        has_errors = True
        print("\n[ERROR] CONSISTENCY ERRORS:")
        print(result.consistency_report)

    # Drift errors
    if result.drift_report and result.drift_report.has_errors:
        has_errors = True
        print("\n[ERROR] DRIFT DETECTED:")
        print(result.drift_report)

    # Parameter mapping errors
    if param_mapping_report and param_mapping_report.has_errors:
        has_errors = True
        print("\n[ERROR] PARAMETER MAPPING ERRORS:")
        # Print only first 10 errors to avoid overwhelming output
        error_mismatches = [m for m in param_mapping_report.mismatches if m.severity == "error"]
        warning_mismatches = [m for m in param_mapping_report.mismatches if m.severity == "warning"]
        
        if error_mismatches:
            print(f"\nFound {len(error_mismatches)} error(s):")
            for mismatch in error_mismatches[:10]:
                print(f"  [ERROR] {mismatch.tool_name} -> {mismatch.method_name}")
                print(f"          {mismatch.parameter_name}: {mismatch.message}")
            if len(error_mismatches) > 10:
                print(f"  ... and {len(error_mismatches) - 10} more errors")
        
        if warning_mismatches:
            print(f"\nFound {len(warning_mismatches)} warning(s):")
            for mismatch in warning_mismatches[:5]:
                print(f"  [WARN] {mismatch.tool_name} -> {mismatch.method_name}")
                print(f"         {mismatch.parameter_name}: {mismatch.message}")
            if len(warning_mismatches) > 5:
                print(f"  ... and {len(warning_mismatches) - 5} more warnings")
        
        print("\nRun: python scripts/validate_parameter_mappings.py --verbose")
        print("For complete parameter mapping validation report.")

    return has_errors


def main():
    """Main entry point for validation script."""
    args = parse_arguments()
    configure_logging(args.verbose, args.quiet)

    # Determine configuration
    validation_mode = determine_validation_mode(args)
    enable_drift = determine_drift_detection(args)
    enable_param_mapping = determine_param_mapping_validation(args)

    logger.info(f"Validation mode: {validation_mode.value}")
    logger.info(f"Drift detection: {'enabled' if enable_drift else 'disabled'}")
    logger.info(f"Parameter mapping: {'enabled' if enable_param_mapping else 'disabled'}")

    try:
        # Create loader with configuration
        loader = RegistryLoader(
            validation_mode=validation_mode,
            enable_drift_detection=enable_drift,
        )

        # Load and validate registries
        logger.info("Starting registry validation...")
        result = loader.load_all_registries()

        # Run parameter mapping validation if enabled
        param_mapping_report = None
        if enable_param_mapping and result.success:
            logger.info("Running parameter mapping validation...")
            try:
                param_mapping_report = validate_parameter_mappings()
                logger.info(f"Parameter mapping: {param_mapping_report.tools_checked} tools checked, "
                          f"{param_mapping_report.error_count} errors, {param_mapping_report.warning_count} warnings")
            except Exception as e:
                logger.error(f"Parameter mapping validation failed: {e}")
                if args.verbose:
                    raise

        # Print summary
        if not args.quiet:
            print_summary(result, param_mapping_report)

        # Print detailed errors if any
        has_errors = print_detailed_errors(result, param_mapping_report)

        # Determine exit code
        if not result.success:
            logger.error("Registry validation failed")
            return 1
        elif has_errors and validation_mode == ValidationMode.STRICT:
            logger.error("Validation errors found in STRICT mode")
            return 1
        else:
            if not args.quiet:
                logger.info("[OK] All validations passed!")
            return 0

    except KeyboardInterrupt:
        logger.error("\n[ERROR] Validation interrupted by user")
        return 2
    except Exception as e:
        logger.error(f"[ERROR] Script execution error: {e}", exc_info=args.verbose)
        return 2


if __name__ == "__main__":
    sys.exit(main())
