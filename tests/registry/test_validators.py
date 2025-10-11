"""
Unit tests for registry validation functions.

Tests coverage validation, consistency validation, and report generation.
"""

from unittest.mock import MagicMock, patch

from src.pydantic_ai_integration.registry.types import (
    ConsistencyReport,
    CoverageReport,
    DriftReport,
)
from src.pydantic_ai_integration.registry.validators import (
    detect_yaml_code_drift,
    validate_method_tool_coverage,
    validate_registry_consistency,
)


class TestCoverageValidation:
    """Test suite for method-tool coverage validation."""

    @patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", {})
    @patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {})
    def test_empty_registries(self):
        """Test validation with empty registries."""
        report = validate_method_tool_coverage()

        assert isinstance(report, CoverageReport)
        assert not report.has_errors
        assert report.error_count == 0
        assert len(report.missing_tools) == 0
        assert len(report.orphaned_tools) == 0

    @patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {})
    def test_methods_without_tools(self):
        """Test detection of methods without corresponding tools."""
        methods = {
            "Service.method1": MagicMock(description="Method 1"),
            "Service.method2": MagicMock(description="Method 2"),
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            report = validate_method_tool_coverage()

            assert report.has_errors
            assert report.error_count == 2
            assert "Service.method1" in report.missing_tools
            assert "Service.method2" in report.missing_tools
            assert len(report.orphaned_tools) == 0

    @patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", {})
    def test_orphaned_tools(self):
        """Test detection of tools without valid method references."""
        tool1 = MagicMock()
        tool1.method_name = "Service.nonexistent_method"

        tool2 = MagicMock()
        tool2.method_name = "Service.another_missing"

        tools = {
            "tool1": tool1,
            "tool2": tool2,
        }

        with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
            report = validate_method_tool_coverage()

            assert report.has_errors
            assert report.error_count == 2
            assert len(report.missing_tools) == 0
            assert "tool1" in report.orphaned_tools
            assert "tool2" in report.orphaned_tools

    def test_perfect_coverage(self):
        """Test validation with 100% method-tool coverage."""
        methods = {
            "Service.method1": MagicMock(description="Method 1"),
            "Service.method2": MagicMock(description="Method 2"),
        }

        tool1 = MagicMock()
        tool1.method_name = "Service.method1"

        tool2 = MagicMock()
        tool2.method_name = "Service.method2"

        tools = {
            "tool1": tool1,
            "tool2": tool2,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
                report = validate_method_tool_coverage()

                assert not report.has_errors
                assert report.error_count == 0
                assert len(report.missing_tools) == 0
                assert len(report.orphaned_tools) == 0

    def test_tool_without_method_reference(self):
        """Test tools that don't have method_name attribute."""
        methods = {
            "Service.method1": MagicMock(description="Method 1"),
        }

        tool1 = MagicMock(spec=[])  # No method_name attribute
        del tool1.method_name

        tools = {
            "tool1": tool1,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
                report = validate_method_tool_coverage()

                # Tool without method_name should leave method orphaned
                assert report.has_errors
                assert "Service.method1" in report.missing_tools

    def test_multiple_tools_for_one_method(self):
        """Test that multiple tools can reference the same method."""
        methods = {
            "Service.method1": MagicMock(description="Method 1"),
        }

        tool1 = MagicMock()
        tool1.method_name = "Service.method1"

        tool2 = MagicMock()
        tool2.method_name = "Service.method1"

        tools = {
            "tool1": tool1,
            "tool2": tool2,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
                report = validate_method_tool_coverage()

                assert not report.has_errors
                assert len(report.missing_tools) == 0


class TestConsistencyValidation:
    """Test suite for registry consistency validation."""

    @patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", {})
    @patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {})
    def test_empty_registries(self):
        """Test validation with empty registries."""
        report = validate_registry_consistency()

        assert isinstance(report, ConsistencyReport)
        assert not report.has_errors
        assert report.error_count == 0

    def test_no_issues(self):
        """Test validation with consistent registries."""
        method1 = MagicMock()
        method1.description = "Method 1 description"
        method1.service = "TestService"

        methods = {
            "Service.method1": method1,
        }

        tool1 = MagicMock()
        tool1.description = "Tool 1 description"

        tools = {
            "tool1": tool1,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
                report = validate_registry_consistency()

                assert not report.has_errors
                assert report.error_count == 0

    def test_method_missing_description(self):
        """Test detection of methods with missing descriptions."""
        method1 = MagicMock()
        method1.description = ""  # Empty description
        method1.service = "TestService"

        methods = {
            "Service.method1": method1,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {}):
                report = validate_registry_consistency()

                assert report.has_errors
                assert any("missing description" in issue for issue in report.issues)

    def test_method_missing_service(self):
        """Test detection of methods with missing service names."""
        method1 = MagicMock()
        method1.description = "Valid description"
        method1.service = ""  # Empty service

        methods = {
            "Service.method1": method1,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {}):
                report = validate_registry_consistency()

                assert report.has_errors
                assert any("missing service" in issue for issue in report.issues)

    def test_tool_missing_description(self):
        """Test detection of tools with missing descriptions."""
        tool1 = MagicMock()
        tool1.description = ""  # Empty description

        tools = {
            "tool1": tool1,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", {}):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", tools):
                report = validate_registry_consistency()

                assert report.has_errors
                assert any("missing description" in issue for issue in report.issues)

    def test_multiple_issues(self):
        """Test detection of multiple consistency issues."""
        method1 = MagicMock()
        method1.description = ""  # Missing description
        method1.service = "TestService"

        method2 = MagicMock()
        method2.description = "Valid"
        method2.service = ""  # Missing service

        methods = {
            "Service.method1": method1,
            "Service.method2": method2,
        }

        with patch("src.pydantic_ai_integration.method_registry.MANAGED_METHODS", methods):
            with patch("src.pydantic_ai_integration.tool_decorator.MANAGED_TOOLS", {}):
                report = validate_registry_consistency()

                assert report.has_errors
                assert report.error_count == 2


class TestDriftDetection:
    """Test suite for YAML-code drift detection."""

    def test_drift_detection_placeholder(self):
        """Test that drift detection returns empty report (Phase 3)."""
        report = detect_yaml_code_drift()

        assert isinstance(report, DriftReport)
        assert not report.has_errors
        assert len(report.missing_in_yaml) == 0
        assert len(report.missing_in_code) == 0
        assert len(report.signature_mismatches) == 0


class TestReportTypes:
    """Test suite for report type functionality."""

    def test_coverage_report_str(self):
        """Test CoverageReport string representation."""
        report = CoverageReport(
            missing_tools=["method1", "method2"],
            orphaned_tools=["tool1"],
            mismatched_signatures=[("tool2", "method3")],
        )

        report_str = str(report)
        assert "Coverage Report" in report_str
        assert "method1" in report_str
        assert "tool1" in report_str

    def test_coverage_report_no_errors(self):
        """Test CoverageReport with no errors."""
        report = CoverageReport()

        assert not report.has_errors
        assert report.error_count == 0
        assert "All checks passed" in str(report)

    def test_consistency_report_str(self):
        """Test ConsistencyReport string representation."""
        report = ConsistencyReport(issues=["Issue 1", "Issue 2"])

        report_str = str(report)
        assert "Consistency Report" in report_str
        assert "Issue 1" in report_str
        assert "Issue 2" in report_str

    def test_consistency_report_no_errors(self):
        """Test ConsistencyReport with no errors."""
        report = ConsistencyReport()

        assert not report.has_errors
        assert report.error_count == 0
        assert "All checks passed" in str(report)

    def test_drift_report_str(self):
        """Test DriftReport string representation."""
        report = DriftReport(
            missing_in_yaml={"method1", "method2"},
            missing_in_code={"method3"},
            signature_mismatches=["method4"],
        )

        report_str = str(report)
        assert "Drift Report" in report_str
        assert "method1" in report_str or "method2" in report_str
        assert "method3" in report_str

    def test_drift_report_no_errors(self):
        """Test DriftReport with no errors."""
        report = DriftReport()

        assert not report.has_errors
        assert report.error_count == 0
        assert "No drift detected" in str(report)

    def test_drift_report_error_count(self):
        """Test DriftReport error count calculation."""
        report = DriftReport(
            missing_in_yaml={"m1", "m2"},
            missing_in_code={"m3"},
            signature_mismatches=["m4", "m5"],
        )

        assert report.error_count == 5  # 2 + 1 + 2
