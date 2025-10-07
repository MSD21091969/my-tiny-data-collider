"""
Test scenario runner for YAML-driven tool testing.

Executes test scenarios defined in tool YAML configurations.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import yaml
from pydantic import BaseModel, ValidationError

from .test_environments import get_test_environment, validate_environment_config
from .tool_test_helper import ToolTestHelper


class TestResult(Enum):
    """Test execution result status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class ScenarioResult:
    """Result of a single test scenario execution."""
    scenario_name: str
    result: TestResult
    execution_time: float
    error_message: Optional[str] = None
    actual_output: Optional[Any] = None
    expected_output: Optional[Any] = None


@dataclass
class TestSuiteResult:
    """Result of a complete test suite execution."""
    tool_name: str
    scenarios: List[ScenarioResult]
    total_scenarios: int
    passed: int
    failed: int
    skipped: int
    errors: int
    execution_time: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_scenarios == 0:
            return 100.0
        return (self.passed / self.total_scenarios) * 100.0


class TestScenarioRunner:
    """Runner for executing YAML-defined test scenarios."""

    def __init__(self):
        """Initialize the test scenario runner."""
        self.results: List[TestSuiteResult] = []

    async def run_tool_scenarios(
        self,
        tool_config_path: Path,
        environment_overrides: Optional[Dict[str, Any]] = None
    ) -> TestSuiteResult:
        """Run all test scenarios for a tool configuration.

        Args:
            tool_config_path: Path to the tool YAML configuration
            environment_overrides: Optional environment variable overrides

        Returns:
            TestSuiteResult with execution details
        """
        import time
        start_time = time.time()

        # Load tool configuration
        try:
            with open(tool_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            return TestSuiteResult(
                tool_name=tool_config_path.stem,
                scenarios=[],
                total_scenarios=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                execution_time=time.time() - start_time
            )

        tool_name = config.get('tool_name', config.get('name', tool_config_path.stem))
        test_scenarios_config = config.get('test_scenarios', {})

        # Handle different test_scenarios structures
        if isinstance(test_scenarios_config, list):
            # Direct list of scenarios
            test_scenarios = test_scenarios_config
        elif isinstance(test_scenarios_config, dict):
            # Nested structure with happy_paths/unhappy_paths
            test_scenarios = []
            for category, scenarios in test_scenarios_config.items():
                if isinstance(scenarios, list):
                    test_scenarios.extend(scenarios)
        else:
            test_scenarios = []

        if not test_scenarios:
            return TestSuiteResult(
                tool_name=tool_name,
                scenarios=[],
                total_scenarios=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                execution_time=time.time() - start_time
            )

        scenario_results = []
        passed = failed = skipped = errors = 0

        for scenario_config in test_scenarios:
            result = await self._run_single_scenario(
                tool_name, scenario_config, environment_overrides
            )
            scenario_results.append(result)

            if result.result == TestResult.PASSED:
                passed += 1
            elif result.result == TestResult.FAILED:
                failed += 1
            elif result.result == TestResult.SKIPPED:
                skipped += 1
            elif result.result == TestResult.ERROR:
                errors += 1

        execution_time = time.time() - start_time

        suite_result = TestSuiteResult(
            tool_name=tool_name,
            scenarios=scenario_results,
            total_scenarios=len(scenario_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            execution_time=execution_time
        )

        self.results.append(suite_result)
        return suite_result

    async def _run_single_scenario(
        self,
        tool_name: str,
        scenario_config: Dict[str, Any],
        environment_overrides: Optional[Dict[str, Any]] = None
    ) -> ScenarioResult:
        """Run a single test scenario.

        Args:
            tool_name: Name of the tool being tested
            scenario_config: Scenario configuration from YAML
            environment_overrides: Optional environment overrides

        Returns:
            ScenarioResult with execution details
        """
        import time
        start_time = time.time()

        scenario_name = scenario_config.get('name', 'unnamed_scenario')
        description = scenario_config.get('description', '')
        skip_reason = scenario_config.get('skip', '')

        # Check if scenario should be skipped
        if skip_reason:
            return ScenarioResult(
                scenario_name=scenario_name,
                result=TestResult.SKIPPED,
                execution_time=time.time() - start_time,
                error_message=skip_reason
            )

        try:
            # Validate scenario configuration
            validation_errors = self._validate_scenario_config(scenario_config)
            if validation_errors:
                return ScenarioResult(
                    scenario_name=scenario_name,
                    result=TestResult.ERROR,
                    execution_time=time.time() - start_time,
                    error_message=f"Configuration validation failed: {', '.join(validation_errors)}"
                )

            # Set up test environment
            env_config = self._setup_test_environment(scenario_config, environment_overrides)

            # Execute the scenario
            result = await self._execute_scenario(tool_name, scenario_config, env_config)

            return ScenarioResult(
                scenario_name=scenario_name,
                result=result[0],
                execution_time=time.time() - start_time,
                error_message=result[1],
                actual_output=result[2],
                expected_output=scenario_config.get('expected_output')
            )

        except Exception as e:
            return ScenarioResult(
                scenario_name=scenario_name,
                result=TestResult.ERROR,
                execution_time=time.time() - start_time,
                error_message=f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
            )

    def _validate_scenario_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate a test scenario configuration.

        Args:
            config: Scenario configuration

        Returns:
            List of validation error messages
        """
        errors = []

        required_fields = ['name']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate environment if specified
        if 'environment' in config:
            env_name = config['environment']
            try:
                env_config = get_test_environment(env_name)
                env_errors = validate_environment_config(env_config)
                errors.extend([f"Environment '{env_name}': {err}" for err in env_errors])
            except ValueError:
                errors.append(f"Unknown test environment: {env_name}")

        # Validate input/output specifications
        if 'input' in config and not isinstance(config['input'], dict):
            errors.append("input must be a dictionary")
        if 'inputs' in config and not isinstance(config['inputs'], dict):
            errors.append("inputs must be a dictionary")

        return errors

    def _setup_test_environment(
        self,
        scenario_config: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Set up the test environment for a scenario.

        Args:
            scenario_config: Scenario configuration
            overrides: Environment overrides

        Returns:
            Environment configuration
        """
        env_name = scenario_config.get('environment', 'valid_user_session')
        env_config = get_test_environment(env_name)

        # Apply overrides
        if overrides:
            env_config.update(overrides)

        # Apply scenario-specific environment settings
        if 'env_vars' in scenario_config:
            env_config.update(scenario_config['env_vars'])

        return env_config

    async def _execute_scenario(
        self,
        tool_name: str,
        scenario_config: Dict[str, Any],
        env_config: Dict[str, Any]
    ) -> Tuple[TestResult, Optional[str], Optional[Any]]:
        """Execute a test scenario.

        Args:
            tool_name: Name of the tool
            scenario_config: Scenario configuration
            env_config: Environment configuration

        Returns:
            Tuple of (result, error_message, actual_output)
        """
        try:
            # Import MANAGED_TOOLS directly
            from pydantic_ai_integration.tools import MANAGED_TOOLS

            if tool_name not in MANAGED_TOOLS:
                return TestResult.ERROR, f"Tool '{tool_name}' not found in MANAGED_TOOLS registry", None

            tool = MANAGED_TOOLS[tool_name]

            # Prepare inputs - handle both 'input' and 'inputs' keys
            inputs = scenario_config.get('inputs') or scenario_config.get('input', {})

            # Execute tool
            if asyncio.iscoroutinefunction(tool.implementation):
                result = await tool.implementation(**inputs)
            else:
                result = tool.implementation(**inputs)

            # Validate result - handle both 'expected_output' and 'expected' keys
            expected_output = scenario_config.get('expected_output') or scenario_config.get('expected')
            if expected_output is not None:
                if self._compare_outputs(result, expected_output):
                    return TestResult.PASSED, None, result
                else:
                    return TestResult.FAILED, f"Output mismatch. Expected: {expected_output}, Got: {result}", result
            else:
                # No expected output specified, consider it passed if no exception
                return TestResult.PASSED, None, result

        except Exception as e:
            error_type = scenario_config.get('expected_error')
            if error_type and isinstance(e, error_type):
                return TestResult.PASSED, None, str(e)
            else:
                return TestResult.FAILED, f"Unexpected error: {str(e)}\n{traceback.format_exc()}", None

    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected outputs.

        Args:
            actual: Actual output
            expected: Expected output (can be simple value or complex conditions)

        Returns:
            True if outputs match
        """
        # Handle complex expected conditions
        if isinstance(expected, dict):
            return self._check_conditions(actual, expected)
        else:
            # Simple equality check
            return actual == expected

    def _check_conditions(self, actual: Any, conditions: Dict[str, Any]) -> bool:
        """Check if actual output meets the expected conditions.

        Args:
            actual: Actual output
            conditions: Dictionary of conditions to check

        Returns:
            True if all conditions are met
        """
        for condition_key, condition_value in conditions.items():
            if not self._check_single_condition(actual, condition_key, condition_value):
                return False
        return True

    def _check_single_condition(self, actual: Any, condition_key: str, condition_value: Any) -> bool:
        """Check a single condition against the actual output.

        Args:
            actual: Actual output
            condition_key: Condition key (e.g., 'status', 'has_casefile_id')
            condition_value: Expected value for the condition

        Returns:
            True if condition is met
        """
        if condition_key == "status":
            return self._get_nested_value(actual, "status") == condition_value
        elif condition_key == "has_casefile_id":
            casefile_id = self._get_nested_value(actual, "casefile_id")
            return (casefile_id is not None) == condition_value
        elif condition_key == "execution_time_under":
            exec_time = self._get_nested_value(actual, "execution_time_ms")
            return exec_time is not None and exec_time < condition_value
        elif condition_key == "title":
            return self._get_nested_value(actual, "title") == condition_value
        elif condition_key == "tags_contain":
            tags = self._get_nested_value(actual, "tags") or []
            return all(tag in tags for tag in condition_value)
        elif condition_key == "error_type":
            error = self._get_nested_value(actual, "error")
            if error and isinstance(error, dict):
                return error.get("type") == condition_value
            return False
        elif condition_key == "error_contains":
            error = self._get_nested_value(actual, "error")
            if error and isinstance(error, str):
                return condition_value in error
            elif error and isinstance(error, dict):
                error_msg = error.get("message", "")
                return condition_value in error_msg
            return False
        else:
            # Unknown condition, treat as direct value check
            return self._get_nested_value(actual, condition_key) == condition_value

    def _get_nested_value(self, obj: Any, key_path: str) -> Any:
        """Get a nested value from an object using dot notation.

        Args:
            obj: Object to extract value from
            key_path: Dot-separated path (e.g., "payload.casefile_id")

        Returns:
            Value at the path, or None if not found
        """
        if not isinstance(obj, dict):
            return None

        keys = key_path.split(".")
        current = obj

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def print_results(self, result: TestSuiteResult, verbose: bool = False):
        """Print test results to console.

        Args:
            result: Test suite result to print
            verbose: Whether to print detailed output
        """
        print(f"\n=== Test Results for {result.tool_name} ===")
        print(f"Total scenarios: {result.total_scenarios}")
        print(f"Passed: {result.passed}")
        print(f"Failed: {result.failed}")
        print(f"Skipped: {result.skipped}")
        print(f"Errors: {result.errors}")
        print(".1f")
        print(f"Execution time: {result.execution_time:.2f}s")

        if verbose and result.scenarios:
            print("\nDetailed Results:")
            for scenario in result.scenarios:
                status_icon = {
                    TestResult.PASSED: "✓",
                    TestResult.FAILED: "✗",
                    TestResult.SKIPPED: "○",
                    TestResult.ERROR: "⚠"
                }.get(scenario.result, "?")

                print(f"  {status_icon} {scenario.scenario_name} ({scenario.execution_time:.2f}s)")
                if scenario.error_message:
                    print(f"    Error: {scenario.error_message}")
                if scenario.result == TestResult.FAILED and verbose:
                    print(f"    Expected: {scenario.expected_output}")
                    print(f"    Actual: {scenario.actual_output}")

    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of all executed test suites.

        Returns:
            Summary report dictionary
        """
        if not self.results:
            return {"total_suites": 0, "total_scenarios": 0}

        total_suites = len(self.results)
        total_scenarios = sum(r.total_scenarios for r in self.results)
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_time = sum(r.execution_time for r in self.results)

        return {
            "total_suites": total_suites,
            "total_scenarios": total_scenarios,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "total_errors": total_errors,
            "total_execution_time": total_time,
            "overall_success_rate": (total_passed / total_scenarios * 100) if total_scenarios > 0 else 100.0,
            "suite_results": [
                {
                    "tool_name": r.tool_name,
                    "scenarios": r.total_scenarios,
                    "passed": r.passed,
                    "failed": r.failed,
                    "skipped": r.skipped,
                    "errors": r.errors,
                    "success_rate": r.success_rate,
                    "execution_time": r.execution_time
                }
                for r in self.results
            ]
        }