"""
Test report generator for YAML-driven tool testing.

Generates detailed HTML and JSON reports from test execution results.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from .test_scenario_runner import TestSuiteResult, TestResult


class TestReportGenerator:
    """Generator for test execution reports."""

    def __init__(self, output_dir: Path):
        """Initialize the report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(
        self,
        results: List[TestSuiteResult],
        report_name: str = "test_report",
        include_details: bool = True
    ) -> Path:
        """Generate an HTML report from test results.

        Args:
            results: List of test suite results
            report_name: Name for the report file
            include_details: Whether to include detailed scenario information

        Returns:
            Path to the generated HTML report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate summary statistics
        total_suites = len(results)
        total_scenarios = sum(r.total_scenarios for r in results)
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_skipped = sum(r.skipped for r in results)
        total_errors = sum(r.errors for r in results)
        total_time = sum(r.execution_time for r in results)

        success_rate = (total_passed / total_scenarios * 100) if total_scenarios > 0 else 100.0

        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {report_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .metric h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 2em;
        }}
        .metric p {{
            margin: 0;
            color: #666;
            font-size: 0.9em;
        }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .errors {{ color: #fd7e14; }}
        .success-rate {{ color: #17a2b8; }}
        .suite-results {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .suite-header {{
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
            font-weight: bold;
        }}
        .suite-row {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr 1fr;
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
            align-items: center;
        }}
        .suite-row:hover {{
            background-color: #f8f9fa;
        }}
        .scenario-details {{
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-passed {{ background: #d4edda; color: #155724; }}
        .status-failed {{ background: #f8d7da; color: #721c24; }}
        .status-skipped {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f5c6cb; color: #721c24; }}
        .expand-btn {{
            background: none;
            border: none;
            color: #007bff;
            cursor: pointer;
            text-decoration: underline;
        }}
        .hidden {{ display: none; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report - {report_name}</h1>
        <p>Generated on {timestamp}</p>
    </div>

    <div class="summary">
        <div class="metric">
            <h3 class="passed">{total_passed}</h3>
            <p>Passed</p>
        </div>
        <div class="metric">
            <h3 class="failed">{total_failed}</h3>
            <p>Failed</p>
        </div>
        <div class="metric">
            <h3 class="skipped">{total_skipped}</h3>
            <p>Skipped</p>
        </div>
        <div class="metric">
            <h3 class="errors">{total_errors}</h3>
            <p>Errors</p>
        </div>
        <div class="metric">
            <h3 class="success-rate">{success_rate:.1f}%</h3>
            <p>Success Rate</p>
        </div>
        <div class="metric">
            <h3>{total_suites}</h3>
            <p>Test Suites</p>
        </div>
        <div class="metric">
            <h3>{total_scenarios}</h3>
            <p>Total Scenarios</p>
        </div>
        <div class="metric">
            <h3>{total_time:.2f}s</h3>
            <p>Execution Time</p>
        </div>
    </div>

    <div class="suite-results">
        <div class="suite-header">
            <div>Test Suite Results</div>
        </div>
"""

        for result in results:
            suite_success_rate = result.success_rate
            suite_class = "passed" if suite_success_rate == 100.0 else "failed"

            html_content += f"""
        <div class="suite-row">
            <div><strong>{result.tool_name}</strong></div>
            <div>{result.total_scenarios}</div>
            <div class="passed">{result.passed}</div>
            <div class="failed">{result.failed}</div>
            <div class="skipped">{result.skipped}</div>
            <div class="errors">{result.errors}</div>
            <div class="{suite_class}">{suite_success_rate:.1f}%</div>
        </div>
"""

            if include_details and result.scenarios:
                html_content += '<div class="scenario-details">'
                for scenario in result.scenarios:
                    status_class = f"status-{scenario.result.value.lower()}"
                    status_icon = {
                        TestResult.PASSED: "✓",
                        TestResult.FAILED: "✗",
                        TestResult.SKIPPED: "○",
                        TestResult.ERROR: "⚠"
                    }.get(scenario.result, "?")

                    html_content += f"""
            <div style="margin-bottom: 8px;">
                <span class="status-badge {status_class}">{status_icon} {scenario.result.value}</span>
                <strong>{scenario.scenario_name}</strong>
                <span style="color: #666;">({scenario.execution_time:.2f}s)</span>
"""

                    if scenario.error_message:
                        html_content += f'<br><small style="color: #dc3545;">{scenario.error_message}</small>'

                    if scenario.result == TestResult.FAILED:
                        html_content += f"""
                        <br><small>Expected: {scenario.expected_output}</small>
                        <br><small>Actual: {scenario.actual_output}</small>
"""

                    html_content += "</div>"

                html_content += "</div>"

        html_content += """
    </div>

    <div class="footer">
        <p>Report generated by YAML Test Executor</p>
    </div>

    <script>
        // Add expand/collapse functionality for scenario details
        document.addEventListener('DOMContentLoaded', function() {
            const suiteRows = document.querySelectorAll('.suite-row');
            suiteRows.forEach(row => {
                const details = row.nextElementSibling;
                if (details && details.classList.contains('scenario-details')) {
                    details.classList.add('hidden');
                    const expandBtn = document.createElement('button');
                    expandBtn.className = 'expand-btn';
                    expandBtn.textContent = 'Show Details';
                    expandBtn.onclick = function() {
                        if (details.classList.contains('hidden')) {
                            details.classList.remove('hidden');
                            this.textContent = 'Hide Details';
                        } else {
                            details.classList.add('hidden');
                            this.textContent = 'Show Details';
                        }
                    };
                    row.appendChild(expandBtn);
                }
            });
        });
    </script>
</body>
</html>"""

        # Save HTML report
        report_path = self.output_dir / f"{report_name}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path

    def generate_json_report(
        self,
        results: List[TestSuiteResult],
        report_name: str = "test_report"
    ) -> Path:
        """Generate a JSON report from test results.

        Args:
            results: List of test suite results
            report_name: Name for the report file

        Returns:
            Path to the generated JSON report
        """
        # Convert results to dictionaries
        results_dict = [asdict(result) for result in results]

        # Add metadata
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "YAML Test Executor",
                "total_suites": len(results),
                "total_scenarios": sum(r.total_scenarios for r in results),
                "total_passed": sum(r.passed for r in results),
                "total_failed": sum(r.failed for r in results),
                "total_skipped": sum(r.skipped for r in results),
                "total_errors": sum(r.errors for r in results),
                "total_execution_time": sum(r.execution_time for r in results)
            },
            "results": results_dict
        }

        # Save JSON report
        report_path = self.output_dir / f"{report_name}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

        return report_path

    def generate_summary_report(
        self,
        results: List[TestSuiteResult],
        report_name: str = "test_summary"
    ) -> Path:
        """Generate a concise summary report.

        Args:
            results: List of test suite results
            report_name: Name for the report file

        Returns:
            Path to the generated summary report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_suites = len(results)
        total_scenarios = sum(r.total_scenarios for r in results)
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_skipped = sum(r.skipped for r in results)
        total_errors = sum(r.errors for r in results)
        total_time = sum(r.execution_time for r in results)

        success_rate = (total_passed / total_scenarios * 100) if total_scenarios > 0 else 100.0

        summary_lines = [
            "=" * 60,
            f"TEST SUMMARY REPORT - {report_name.upper()}",
            "=" * 60,
            f"Generated: {timestamp}",
            "",
            "OVERALL RESULTS:",
            f"  Total Test Suites: {total_suites}",
            f"  Total Scenarios:   {total_scenarios}",
            f"  Passed:           {total_passed}",
            f"  Failed:           {total_failed}",
            f"  Skipped:          {total_skipped}",
            f"  Errors:           {total_errors}",
            ".1f",
            f"  Execution Time:   {total_time:.2f}s",
            "",
            "SUITE DETAILS:",
        ]

        for result in results:
            summary_lines.extend([
                f"  {result.tool_name}:",
                f"    Scenarios: {result.total_scenarios}, "
                f"Passed: {result.passed}, Failed: {result.failed}, "
                f"Skipped: {result.skipped}, Errors: {result.errors} "
                ".1f",
            ])

        summary_lines.extend([
            "",
            "=" * 60,
            "Report generated by YAML Test Executor",
            "=" * 60
        ])

        summary_content = "\n".join(summary_lines)

        # Save summary report
        report_path = self.output_dir / f"{report_name}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        return report_path

    def generate_all_reports(
        self,
        results: List[TestSuiteResult],
        base_name: str = "test_report"
    ) -> Dict[str, Path]:
        """Generate all report types (HTML, JSON, summary).

        Args:
            results: List of test suite results
            base_name: Base name for report files

        Returns:
            Dictionary mapping report types to file paths
        """
        reports = {}

        try:
            reports['html'] = self.generate_html_report(results, base_name)
        except Exception as e:
            print(f"Failed to generate HTML report: {e}", file=sys.stderr)

        try:
            reports['json'] = self.generate_json_report(results, base_name)
        except Exception as e:
            print(f"Failed to generate JSON report: {e}", file=sys.stderr)

        try:
            reports['summary'] = self.generate_summary_report(results, base_name)
        except Exception as e:
            print(f"Failed to generate summary report: {e}", file=sys.stderr)

        return reports