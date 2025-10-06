"""
System-Wide Automated Test Runner

Orchestrates all validation tests and generates comprehensive reports.
Run this to validate the entire system after refactoring.
"""

import sys
from pathlib import Path
import pytest
import json
from datetime import datetime
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


class SystemValidationRunner:
    """Orchestrates system-wide validation tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.report_dir = PROJECT_ROOT / "test_reports"
        self.report_dir.mkdir(exist_ok=True)
        
        self.test_suites = [
            ("Code Integrity", "test_code_integrity.py"),
            ("Type Validation", "test_type_validation.py"),
            ("YAML Validation", "test_yaml_validation.py"),
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation test suites."""
        print("\n" + "="*80)
        print("SYSTEM-WIDE VALIDATION TEST SUITE")
        print("="*80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Project: {PROJECT_ROOT.name}")
        print("="*80 + "\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(PROJECT_ROOT),
            "suites": []
        }
        
        for suite_name, test_file in self.test_suites:
            print(f"\n{'='*80}")
            print(f"Running: {suite_name}")
            print(f"{'='*80}")
            
            test_path = self.test_dir / test_file
            
            # Run pytest and capture results
            exit_code = pytest.main([
                str(test_path),
                "-v",
                "-s",
                "--tb=short",
                f"--junit-xml={self.report_dir / f'{test_file}.xml'}"
            ])
            
            suite_result = {
                "name": suite_name,
                "file": test_file,
                "exit_code": exit_code,
                "status": "PASSED" if exit_code == 0 else "FAILED"
            }
            
            results["suites"].append(suite_result)
            
            print(f"\n{suite_name}: {'✅ PASSED' if exit_code == 0 else '❌ FAILED'}")
        
        return results
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary report."""
        lines = []
        lines.append("="*80)
        lines.append("SYSTEM VALIDATION SUMMARY REPORT")
        lines.append("="*80)
        lines.append(f"Timestamp: {results['timestamp']}")
        lines.append(f"Project: {Path(results['project_root']).name}")
        lines.append("")
        
        total_suites = len(results["suites"])
        passed_suites = sum(1 for s in results["suites"] if s["status"] == "PASSED")
        failed_suites = total_suites - passed_suites
        
        lines.append(f"Total Test Suites: {total_suites}")
        lines.append(f"Passed: {passed_suites}")
        lines.append(f"Failed: {failed_suites}")
        lines.append(f"Success Rate: {(passed_suites/total_suites*100):.2f}%")
        lines.append("")
        lines.append("-"*80)
        lines.append("SUITE DETAILS")
        lines.append("-"*80)
        
        for suite in results["suites"]:
            status_icon = "✅" if suite["status"] == "PASSED" else "❌"
            lines.append(f"{status_icon} {suite['name']:<30} {suite['status']}")
        
        lines.append("")
        lines.append("="*80)
        
        if failed_suites == 0:
            lines.append("🎉 ALL VALIDATION TESTS PASSED!")
            lines.append("System is ready for commit and deployment.")
        else:
            lines.append("⚠️  VALIDATION FAILURES DETECTED")
            lines.append(f"Please review failed test suites before committing.")
        
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def save_json_report(self, results: Dict[str, Any]):
        """Save results as JSON for analysis."""
        report_path = self.report_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 JSON Report saved: {report_path.relative_to(PROJECT_ROOT)}")
    
    def save_text_report(self, summary: str):
        """Save summary as text file."""
        report_path = self.report_dir / f"validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"📄 Text Report saved: {report_path.relative_to(PROJECT_ROOT)}")


def main():
    """Main entry point for system validation."""
    runner = SystemValidationRunner()
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Generate summary
    summary = runner.generate_summary_report(results)
    print("\n" + summary)
    
    # Save reports
    runner.save_json_report(results)
    runner.save_text_report(summary)
    
    # Exit with appropriate code
    failed_count = sum(1 for s in results["suites"] if s["status"] == "FAILED")
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
