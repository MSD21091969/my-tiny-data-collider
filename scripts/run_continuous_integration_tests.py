"""
Continuous integration test runner for casefile tools.

Runs comprehensive test suite continuously with auto-approval.
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
    """Runs integration tests continuously with comprehensive logging."""

    def __init__(self):
        self.run_count = 0
        self.total_passed = 0
        self.total_failed = 0
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
                   passed: int, failed: int, output: str):
        """Log the end of a test run."""
        logger.info(f"=== TEST RUN #{run_number} COMPLETED ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Result: {'PASS' if success else 'FAIL'}")
        logger.info(f"Tests: {passed} passed, {failed} failed")

        # Save detailed results
        result_file = self.results_dir / f"run_{run_number:03d}_{'pass' if success else 'fail'}.json"
        result_data = {
            "run_number": run_number,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "success": success,
            "passed": passed,
            "failed": failed,
            "output": output[-5000:] if len(output) > 5000 else output  # Last 5k chars
        }

        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)

    def analyze_output(self, output: str) -> tuple[int, int]:
        """Analyze pytest output to extract pass/fail counts."""
        lines = output.split('\n')
        passed = 0
        failed = 0

        for line in lines:
            if 'passed' in line and 'failed' in line:
                # Parse line like "5 passed, 0 failed"
                parts = line.strip().split(',')
                for part in parts:
                    part = part.strip()
                    if 'passed' in part:
                        try:
                            passed = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif 'failed' in part:
                        try:
                            failed = int(part.split()[0])
                        except (ValueError, IndexError):
                            pass

        return passed, failed

    def extract_error_patterns(self, output: str):
        """Extract and count error patterns from test output."""
        # Look for common error patterns
        error_indicators = [
            "ImportError",
            "AssertionError",
            "ValueError",
            "RuntimeError",
            "ConnectionError",
            "TimeoutError",
            "FAILED",
            "ERROR"
        ]

        for indicator in error_indicators:
            if indicator in output:
                if indicator not in self.error_patterns:
                    self.error_patterns[indicator] = 0
                self.error_patterns[indicator] += 1

    def run_single_test(self) -> tuple[bool, float, int, int, str]:
        """Run a single test iteration."""
        start_time = time.time()

        try:
            # Run pytest on the integration test suite
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_casefile_tools_integration.py",
                "-v", "--tb=short", "--capture=no"
            ]

            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            duration = time.time() - start_time
            output = result.stdout + result.stderr
            success = result.returncode == 0

            passed, failed = self.analyze_output(output)
            self.extract_error_patterns(output)

            return success, duration, passed, failed, output

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error("Test run timed out after 5 minutes")
            return False, duration, 0, 0, "TIMEOUT: Test run exceeded 5 minutes"

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Test run failed with exception: {e}")
            return False, duration, 0, 0, f"EXCEPTION: {str(e)}"

    def print_summary(self):
        """Print comprehensive test summary."""
        total_runtime = datetime.now() - self.start_time
        success_rate = (self.total_passed / max(self.total_passed + self.total_failed, 1)) * 100

        logger.info("=" * 60)
        logger.info("CONTINUOUS TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total runs: {self.run_count}")
        logger.info(f"Total runtime: {total_runtime}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Total passed: {self.total_passed}")
        logger.info(f"Total failed: {self.total_failed}")
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

    def run_continuous(self, max_runs: int = None):
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
                success, duration, passed, failed, output = self.run_single_test()

                self.total_passed += passed
                self.total_failed += failed
                self.performance_stats.append(duration)

                self.log_run_end(self.run_count, success, duration, passed, failed, output)

                # Brief pause between runs
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Tests interrupted by user")
        finally:
            self.print_summary()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Continuous Casefile Tools Integration Tester")
    parser.add_argument("--max-runs", type=int, default=None,
                       help="Maximum number of test runs (default: unlimited)")
    parser.add_argument("--single-run", action="store_true",
                       help="Run a single test and exit")

    args = parser.parse_args()

    runner = ContinuousTestRunner()

    if args.single_run:
        logger.info("Running single test...")
        success, duration, passed, failed, output = runner.run_single_test()
        runner.log_run_end(1, success, duration, passed, failed, output)
        runner.print_summary()
    else:
        runner.run_continuous(args.max_runs)


if __name__ == "__main__":
    main()