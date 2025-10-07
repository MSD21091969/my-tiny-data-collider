#!/usr/bin/env python3
"""
YAML Test Executor - Main entry point for running YAML-driven tool tests.

Usage:
    python -m tests.helpers.test_runner [options] <tool_config_files...>

Examples:
    # Run tests for a specific tool
    python -m tests.helpers.test_runner config/toolsets/core/casefile_management/create_casefile_inherited.yaml

    # Run tests for all tools in a directory
    python -m tests.helpers.test_runner config/toolsets/**/*.yaml

    # Run with verbose output and custom report name
    python -m tests.helpers.test_runner -v -r my_test_report config/toolsets/**/*.yaml

    # Run with environment overrides
    python -m tests.helpers.test_runner --env user_id=test_user_123 config/toolsets/**/*.yaml
"""

import argparse
import asyncio
import glob
import sys
from pathlib import Path
from typing import List, Optional

# Import generated tools to register them in MANAGED_TOOLS
try:
    from scripts.import_generated_tools import import_all_generated_modules
    import_all_generated_modules()
except Exception as e:
    print(f"Warning: Failed to import generated tools: {e}", file=sys.stderr)

from .test_scenario_runner import TestScenarioRunner
from .test_report_generator import TestReportGenerator


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="YAML Test Executor - Run YAML-driven tool tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='YAML tool configuration files or glob patterns'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-r', '--report-name',
        default='test_report',
        help='Base name for generated reports (default: test_report)'
    )

    parser.add_argument(
        '--reports-dir',
        default='tests/reports',
        help='Directory to save reports (default: tests/reports)'
    )

    parser.add_argument(
        '--env',
        action='append',
        help='Environment variable overrides in format KEY=VALUE'
    )

    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )

    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Skip JSON report generation'
    )

    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip summary report generation'
    )

    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop execution on first failure'
    )

    return parser.parse_args()


def expand_glob_patterns(patterns: List[str]) -> List[Path]:
    """Expand glob patterns to file paths.

    Args:
        patterns: List of file paths or glob patterns

    Returns:
        List of expanded file paths
    """
    expanded_files = []

    for pattern in patterns:
        path = Path(pattern)

        # If it's a direct file path, check if it exists
        if path.is_file():
            expanded_files.append(path)
        else:
            # Try glob expansion
            matches = glob.glob(str(pattern), recursive=True)
            for match in matches:
                match_path = Path(match)
                if match_path.is_file() and match_path.suffix.lower() in ['.yaml', '.yml']:
                    expanded_files.append(match_path)

    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file_path in expanded_files:
        if file_path not in seen:
            seen.add(file_path)
            unique_files.append(file_path)

    return unique_files


def parse_env_overrides(env_args: Optional[List[str]]) -> dict:
    """Parse environment variable overrides from command line args.

    Args:
        env_args: List of KEY=VALUE strings

    Returns:
        Dictionary of environment overrides
    """
    overrides = {}

    if not env_args:
        return overrides

    for env_arg in env_args:
        if '=' not in env_arg:
            print(f"Warning: Invalid environment override format: {env_arg} (expected KEY=VALUE)",
                  file=sys.stderr)
            continue

        key, value = env_arg.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Try to parse as JSON for complex values
        try:
            import json
            parsed_value = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            # Keep as string if not valid JSON
            parsed_value = value

        overrides[key] = parsed_value

    return overrides


async def run_tests(
    config_files: List[Path],
    environment_overrides: Optional[dict] = None,
    fail_fast: bool = False,
    verbose: bool = False
) -> List:
    """Run tests for the specified configuration files.

    Args:
        config_files: List of YAML configuration file paths
        environment_overrides: Optional environment variable overrides
        fail_fast: Whether to stop on first failure
        verbose: Whether to enable verbose output

    Returns:
        List of TestSuiteResult objects
    """
    runner = TestScenarioRunner()
    results = []

    for config_file in config_files:
        if verbose:
            print(f"\nRunning tests for: {config_file}")

        try:
            result = await runner.run_tool_scenarios(config_file, environment_overrides)
            results.append(result)

            if verbose:
                runner.print_results(result, verbose=True)

            # Check for failures if fail-fast is enabled
            if fail_fast and (result.failed > 0 or result.errors > 0):
                print(f"\nStopping execution due to failures in {config_file}")
                break

        except Exception as e:
            print(f"Error running tests for {config_file}: {e}", file=sys.stderr)
            if fail_fast:
                break

    return results


def generate_reports(
    results: List,
    report_name: str,
    reports_dir: Path,
    skip_html: bool = False,
    skip_json: bool = False,
    skip_summary: bool = False,
    verbose: bool = False
) -> dict:
    """Generate test reports.

    Args:
        results: List of TestSuiteResult objects
        report_name: Base name for reports
        reports_dir: Directory to save reports
        skip_html: Whether to skip HTML report
        skip_json: Whether to skip JSON report
        skip_summary: Whether to skip summary report
        verbose: Whether to enable verbose output

    Returns:
        Dictionary of generated report paths
    """
    if not results:
        print("No test results to report")
        return {}

    generator = TestReportGenerator(reports_dir)
    reports = {}

    if not skip_html:
        try:
            html_path = generator.generate_html_report(results, report_name)
            reports['html'] = html_path
            if verbose:
                print(f"HTML report generated: {html_path}")
        except Exception as e:
            print(f"Failed to generate HTML report: {e}", file=sys.stderr)

    if not skip_json:
        try:
            json_path = generator.generate_json_report(results, report_name)
            reports['json'] = json_path
            if verbose:
                print(f"JSON report generated: {json_path}")
        except Exception as e:
            print(f"Failed to generate JSON report: {e}", file=sys.stderr)

    if not skip_summary:
        try:
            summary_path = generator.generate_summary_report(results, report_name)
            reports['summary'] = summary_path
            if verbose:
                print(f"Summary report generated: {summary_path}")
        except Exception as e:
            print(f"Failed to generate summary report: {e}", file=sys.stderr)

    return reports


def print_summary(results: List, verbose: bool = False):
    """Print a summary of test results to console.

    Args:
        results: List of TestSuiteResult objects
        verbose: Whether to enable verbose output
    """
    if not results:
        print("No tests were executed.")
        return

    total_suites = len(results)
    total_scenarios = sum(r.total_scenarios for r in results)
    total_passed = sum(r.passed for r in results)
    total_failed = sum(r.failed for r in results)
    total_skipped = sum(r.skipped for r in results)
    total_errors = sum(r.errors for r in results)
    total_time = sum(r.execution_time for r in results)

    success_rate = (total_passed / total_scenarios * 100) if total_scenarios > 0 else 100.0

    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Test Suites:     {total_suites}")
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Passed:         {total_passed}")
    print(f"Failed:         {total_failed}")
    print(f"Skipped:        {total_skipped}")
    print(f"Errors:         {total_errors}")
    print(".1f")
    print(f"Execution Time: {total_time:.2f}s")
    print("="*60)

    if verbose and results:
        print("\nSuite Details:")
        for result in results:
            status = "✓" if result.success_rate == 100.0 else "✗"
            print(f"  {status} {result.tool_name}: {result.passed}/{result.total_scenarios} passed "
                  ".1f")


def main():
    """Main entry point."""
    args = parse_args()

    # Expand file patterns
    config_files = expand_glob_patterns(args.files)

    if not config_files:
        print("No YAML configuration files found matching the specified patterns.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Found {len(config_files)} configuration files:")
        for file_path in config_files:
            print(f"  {file_path}")

    # Parse environment overrides
    env_overrides = parse_env_overrides(args.env)

    # Create reports directory
    reports_dir = Path(args.reports_dir)

    try:
        # Run the tests
        if args.verbose:
            print("\nExecuting tests...")

        results = asyncio.run(run_tests(
            config_files=config_files,
            environment_overrides=env_overrides,
            fail_fast=args.fail_fast,
            verbose=args.verbose
        ))

        # Generate reports
        if results:
            reports = generate_reports(
                results=results,
                report_name=args.report_name,
                reports_dir=reports_dir,
                skip_html=args.no_html,
                skip_json=args.no_json,
                skip_summary=args.no_summary,
                verbose=args.verbose
            )

            if args.verbose and reports:
                print(f"\nReports saved to: {reports_dir}")
                for report_type, path in reports.items():
                    print(f"  {report_type.upper()}: {path.name}")

        # Print summary
        print_summary(results, args.verbose)

        # Determine exit code based on results
        total_failed = sum(r.failed for r in results)
        total_errors = sum(r.errors for r in results)

        if total_failed > 0 or total_errors > 0:
            sys.exit(1)  # Exit with error code if there were failures

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()