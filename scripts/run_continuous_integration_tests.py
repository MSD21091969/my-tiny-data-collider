"""
Continuous integration test runner for casefile tools.

Runs comprehensive test suite continuously with auto-approval using the new YAML-driven test approach.
Logs all results, errors, and behavior patterns for analysis.
"""

import subprocess
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import signal
import os
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/integration_test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContinuousTestRunner:
    """Runs integration tests continuously with comprehensive logging using YAML-driven testing."""

    def __init__(self):
        self.run_count = 0
        self.total_passed = 0
        self.total_failed = 0
        self.total_errors = 0
        self.total_skipped = 0
        self.error_patterns = {}
        self.performance_stats = []
        self.start_time = datetime.now()
        self.results_dir = Path("tests/integration_logs")
        self.results_dir.mkdir(exist_ok=True)

    def log_run_start(self, run_number: int):
        """Log the start of a test run."""
        logger.info(f"=== STARTING TEST RUN #{run_number} ===")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")

    def log_run_end(self, run_number: int, success: bool, duration: float,
                   results_summary: dict, output: str):
        """Log the end of a test run."""
        logger.info(f"=== TEST RUN #{run_number} COMPLETED ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Result: {'PASS' if success else 'FAIL'}")
        logger.info(f"Test Suites: {results_summary.get('total_suites', 0)}")
        logger.info(f"Scenarios: {results_summary.get('total_scenarios', 0)} passed, "
                   f"{results_summary.get('total_failed', 0)} failed, "
                   f"{results_summary.get('total_errors', 0)} errors, "
                   f"{results_summary.get('total_skipped', 0)} skipped")

        # Save detailed results
        result_file = self.results_dir / f"run_{run_number:03d}_{'pass' if success else 'fail'}.json"
        result_data = {
            "run_number": run_number,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "success": success,
            "results_summary": results_summary,
            "output": output[-5000:] if len(output) > 5000 else output  # Last 5k chars
        }

        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)

    def analyze_results(self, results: list) -> dict:
        """Analyze test results to extract summary statistics."""
        if not results:
            return {
                "total_suites": 0,
                "total_scenarios": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_errors": 0,
                "total_skipped": 0,
                "overall_success_rate": 0.0
            }

        total_suites = len(results)
        total_scenarios = sum(r.get('total_scenarios', 0) for r in results)
        total_passed = sum(r.get('passed', 0) for r in results)
        total_failed = sum(r.get('failed', 0) for r in results)
        total_errors = sum(r.get('errors', 0) for r in results)
        total_skipped = sum(r.get('skipped', 0) for r in results)

        overall_success_rate = (total_passed / total_scenarios * 100) if total_scenarios > 0 else 100.0

        return {
            "total_suites": total_suites,
            "total_scenarios": total_scenarios,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
            "overall_success_rate": overall_success_rate
        }

    def extract_error_patterns(self, output: str):
        """Extract and count error patterns from test output."""
        # Look for common error patterns in YAML-driven test output
        error_indicators = [
            "ImportError",
            "AssertionError",
            "ValueError",
            "RuntimeError",
            "ConnectionError",
            "TimeoutError",
            "FAILED",
            "ERROR",
            "Tool not found",
            "Configuration validation failed",
            "Unexpected error"
        ]

        for indicator in error_indicators:
            if indicator in output:
                if indicator not in self.error_patterns:
                    self.error_patterns[indicator] = 0
                self.error_patterns[indicator] += 1

    async def run_single_test(self) -> tuple[bool, float, dict, str]:
        """Run a single test iteration using the YAML-driven test runner."""
        start_time = time.time()

        try:
            # Import the test runner
            from tests.helpers.test_scenario_runner import TestScenarioRunner

            # Find all tool configuration files
            config_pattern = "config/toolsets/**/*.yaml"
            config_files = list(Path().glob(config_pattern))

            if not config_files:
                logger.warning("No tool configuration files found")
                duration = time.time() - start_time
                return False, duration, {}, "No configuration files found"

            logger.info(f"Found {len(config_files)} tool configuration files")

            # Run tests using the YAML-driven approach
            runner = TestScenarioRunner()
            results = []

            for config_file in config_files:
                try:
                    result = await runner.run_tool_scenarios(config_file)
                    results.append({
                        "tool_name": result.tool_name,
                        "total_scenarios": result.total_scenarios,
                        "passed": result.passed,
                        "failed": result.failed,
                        "skipped": result.skipped,
                        "errors": result.errors,
                        "execution_time": result.execution_time
                    })
                except Exception as e:
                    logger.error(f"Failed to run tests for {config_file}: {e}")
                    results.append({
                        "tool_name": config_file.stem,
                        "total_scenarios": 0,
                        "passed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "errors": 1,
                        "execution_time": 0.0
                    })

            duration = time.time() - start_time
            results_summary = self.analyze_results(results)

            # Update cumulative counters
            self.total_passed += results_summary["total_passed"]
            self.total_failed += results_summary["total_failed"]
            self.total_errors += results_summary["total_errors"]
            self.total_skipped += results_summary["total_skipped"]

            # Determine success (no failures or errors)
            success = results_summary["total_failed"] == 0 and results_summary["total_errors"] == 0

            # Generate output summary
            output = f"Test execution completed. Success: {success}\n"
            output += f"Results: {results_summary}\n"
            for result in results:
                output += f"  {result['tool_name']}: {result['passed']}/{result['total_scenarios']} passed\n"

            self.extract_error_patterns(output)

            return success, duration, results_summary, output

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Test run failed with exception: {e}")
            error_output = f"EXCEPTION: {str(e)}"
            self.extract_error_patterns(error_output)
            return False, duration, {}, error_output

    def print_summary(self):
        """Print comprehensive test summary."""
        total_runtime = datetime.now() - self.start_time
        total_scenarios = self.total_passed + self.total_failed + self.total_errors + self.total_skipped
        success_rate = (self.total_passed / max(total_scenarios, 1)) * 100

        logger.info("=" * 60)
        logger.info("CONTINUOUS TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total runs: {self.run_count}")
        logger.info(f"Total runtime: {total_runtime}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Total scenarios: {total_scenarios}")
        logger.info(f"Total passed: {self.total_passed}")
        logger.info(f"Total failed: {self.total_failed}")
        logger.info(f"Total errors: {self.total_errors}")
        logger.info(f"Total skipped: {self.total_skipped}")
        logger.info("")
        logger.info("Error Patterns:")
        for error, count in sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {error}: {count} occurrences")
        logger.info("")
        logger.info("Performance Stats:")
        if self.performance_stats:
            avg_duration = sum(self.performance_stats) / len(self.performance_stats)
            min_duration = min(self.performance_stats)
            max_duration = max(self.performance_stats)
            logger.info(f"  Average duration: {avg_duration:.2f}s")
            logger.info(f"  Min duration: {min_duration:.2f}s")
            logger.info(f"  Max duration: {max_duration:.2f}s")
        logger.info("=" * 60)

    async def run_continuous_async(self, max_runs: int = None):
        """Run tests continuously until interrupted or max_runs reached."""
        logger.info("Starting continuous integration test runner")
        logger.info("Press Ctrl+C to stop testing")
        logger.info("=" * 60)

        def signal_handler(signum, frame):
            logger.info("Received interrupt signal, stopping tests...")
            self.print_summary()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            while max_runs is None or self.run_count < max_runs:
                self.run_count += 1

                self.log_run_start(self.run_count)
                success, duration, results_summary, output = await self.run_single_test()

                self.performance_stats.append(duration)

                self.log_run_end(self.run_count, success, duration, results_summary, output)

                # Brief pause between runs
                await asyncio.sleep(2)

        except KeyboardInterrupt:
            logger.info("Tests interrupted by user")
        finally:
            self.print_summary()

    def run_continuous(self, max_runs: int = None):
        """Synchronous wrapper for continuous testing."""
        asyncio.run(self.run_continuous_async(max_runs))


async def main_async():
    """Main entry point with async support."""
    import argparse

    parser = argparse.ArgumentParser(description="Continuous Casefile Tools Integration Tester")
    parser.add_argument("--max-runs", type=int, default=None,
                       help="Maximum number of test runs (default: unlimited)")
    parser.add_argument("--single-run", action="store_true",
                       help="Run a single test and exit")
    parser.add_argument("--config-pattern", default="config/toolsets/**/*.yaml",
                       help="Glob pattern for tool configuration files")

    args = parser.parse_args()

    runner = ContinuousTestRunner()

    if args.single_run:
        logger.info("Running single test...")
        success, duration, results_summary, output = await runner.run_single_test()
        runner.log_run_end(1, success, duration, results_summary, output)
        runner.print_summary()
    else:
        runner.run_continuous(args.max_runs)


def main():
    """Synchronous main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()