"""
YAML-Driven Test Execution Engine

Executes test scenarios defined in tool YAML configurations.
Replaces multiple overlapping test layers with single YAML-driven approach.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import asyncio
from dataclasses import dataclass
from enum import Enum

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pydantic_ai_integration.dependencies import MDSContext
from pydantic_ai_integration.tools import MANAGED_TOOLS


class TestResult(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


@dataclass
class ScenarioResult:
    scenario_name: str
    result: TestResult
    execution_time_ms: float
    actual_output: Any
    expected_output: Any
    error_message: Optional[str] = None


@dataclass
class TestEnvironment:
    user_id: str
    session_id: str
    permissions: List[str]
    session_valid: bool = True
    token_valid: bool = True


class YAMLTestExecutor:
    """Executes test scenarios defined in YAML tool configurations."""

    def __init__(self):
        self.environments: Dict[str, TestEnvironment] = {}
        self.results: List[ScenarioResult] = []

    def load_test_scenarios(self, yaml_path: Path) -> Dict[str, Any]:
        """Load test scenarios from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Extract test scenarios and environments
        if 'test_scenarios' in config:
            scenarios = config['test_scenarios']
            if 'environments' in scenarios:
                self._load_environments(scenarios['environments'])
            return scenarios
        return {}

    def _load_environments(self, env_config: Dict[str, Any]):
        """Load test environment fixtures."""
        for env_name, env_data in env_config.items():
            self.environments[env_name] = TestEnvironment(
                user_id=env_data['user_id'],
                session_id=env_data['session_id'],
                permissions=env_data['permissions'],
                session_valid=env_data.get('session_valid', True),
                token_valid=env_data.get('token_valid', True)
            )

    async def execute_scenario(self, tool_name: str, scenario: Dict[str, Any]) -> ScenarioResult:
        """Execute a single test scenario."""
        import time
        start_time = time.time()

        try:
            # Get environment
            env_name = scenario['environment']
            if env_name not in self.environments:
                return ScenarioResult(
                    scenario_name=scenario['name'],
                    result=TestResult.ERROR,
                    execution_time_ms=0,
                    actual_output=None,
                    expected_output=scenario.get('expected'),
                    error_message=f"Environment '{env_name}' not defined"
                )

            env = self.environments[env_name]

            # Create MDS context
            ctx = MDSContext(
                user_id=env.user_id,
                session_id=env.session_id,
                tool_name=tool_name,
                request_id=f"test_{scenario['name']}_{env.session_id}",
                permissions=env.permissions,
                metadata={"test_mode": True}
            )

            # Get tool
            if tool_name not in MANAGED_TOOLS:
                return ScenarioResult(
                    scenario_name=scenario['name'],
                    result=TestResult.ERROR,
                    execution_time_ms=0,
                    actual_output=None,
                    expected_output=scenario.get('expected'),
                    error_message=f"Tool '{tool_name}' not found"
                )

            tool = MANAGED_TOOLS[tool_name]

            # Execute tool
            try:
                result = await tool.implementation(ctx, **scenario['input'])
                execution_time = (time.time() - start_time) * 1000

                # Validate result against expectations
                is_passed = self._validate_result(result, scenario['expected'])

                return ScenarioResult(
                    scenario_name=scenario['name'],
                    result=TestResult.PASSED if is_passed else TestResult.FAILED,
                    execution_time_ms=execution_time,
                    actual_output=result,
                    expected_output=scenario['expected']
                )

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                return ScenarioResult(
                    scenario_name=scenario['name'],
                    result=TestResult.FAILED,
                    execution_time_ms=execution_time,
                    actual_output=None,
                    expected_output=scenario['expected'],
                    error_message=str(e)
                )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ScenarioResult(
                scenario_name=scenario['name'],
                result=TestResult.ERROR,
                execution_time_ms=execution_time,
                actual_output=None,
                expected_output=scenario.get('expected'),
                error_message=f"Test execution error: {str(e)}"
            )

    def _validate_result(self, actual: Any, expected: Dict[str, Any]) -> bool:
        """Validate actual result against expected criteria."""
        try:
            for key, expected_value in expected.items():
                if key == 'status':
                    if actual.get('status') != expected_value:
                        return False
                elif key == 'has_casefile_id':
                    if expected_value and 'casefile_id' not in actual:
                        return False
                elif key == 'execution_time_under':
                    if actual.get('execution_time_ms', 0) > expected_value:
                        return False
                elif key == 'tags_contain':
                    actual_tags = actual.get('tags', [])
                    if not all(tag in actual_tags for tag in expected_value):
                        return False
                elif key == 'error_type':
                    # For error scenarios, check if error matches expected type
                    if 'error' not in actual or expected_value not in str(actual['error']):
                        return False
                elif key == 'error_contains':
                    if 'error' not in actual or expected_value not in str(actual['error']):
                        return False
                elif key in actual and actual[key] != expected_value:
                    return False
            return True
        except Exception:
            return False

    async def execute_tool_tests(self, yaml_path: Path) -> List[ScenarioResult]:
        """Execute all test scenarios for a tool."""
        config = self.load_test_scenarios(yaml_path)
        if not config:
            return []

        tool_name = yaml_path.stem  # Remove .yaml extension
        results = []

        # Execute happy paths
        for scenario in config.get('happy_paths', []):
            result = await self.execute_scenario(tool_name, scenario)
            results.append(result)

        # Execute unhappy paths
        for scenario in config.get('unhappy_paths', []):
            result = await self.execute_scenario(tool_name, scenario)
            results.append(result)

        return results

    def print_results(self, results: List[ScenarioResult]):
        """Print test results in a readable format."""
        print(f"\n{'='*60}")
        print("YAML-DRIVEN TEST RESULTS")
        print(f"{'='*60}")

        passed = sum(1 for r in results if r.result == TestResult.PASSED)
        failed = sum(1 for r in results if r.result == TestResult.FAILED)
        errors = sum(1 for r in results if r.result == TestResult.ERROR)

        print(f"Total Scenarios: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print()

        for result in results:
            status_icon = {
                TestResult.PASSED: "✅",
                TestResult.FAILED: "❌",
                TestResult.ERROR: "🔥"
            }[result.result]

            print(f"{status_icon} {result.scenario_name}")
            print(f"   Duration: {result.execution_time_ms:.2f}ms")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            print()


async def main():
    """Main execution function."""
    if len(sys.argv) != 2:
        print("Usage: python yaml_test_executor.py <tool_yaml_path>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])
    if not yaml_path.exists():
        print(f"Error: YAML file not found: {yaml_path}")
        sys.exit(1)

    executor = YAMLTestExecutor()
    results = await executor.execute_tool_tests(yaml_path)
    executor.print_results(results)

    # Exit with appropriate code
    failed_or_error = any(r.result in [TestResult.FAILED, TestResult.ERROR] for r in results)
    sys.exit(1 if failed_or_error else 0)


if __name__ == "__main__":
    asyncio.run(main())