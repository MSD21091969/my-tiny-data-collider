"""
Shared types and models for registry system.

Defines validation modes, result types, and report structures used across
the registry loading and validation system.
"""

from dataclasses import dataclass, field
from enum import Enum


class ValidationMode(str, Enum):
    """
    Validation strictness mode.

    Attributes:
        STRICT: Raise exceptions on validation failures (CI/CD mode)
        WARNING: Log warnings but continue (development mode)
    """

    STRICT = "strict"
    WARNING = "warning"


@dataclass
class CoverageReport:
    """
    Method-to-tool coverage validation report.

    Validates that every method has a corresponding tool and vice versa.

    Attributes:
        missing_tools: Methods without corresponding tools
        orphaned_tools: Tools without valid method references
        mismatched_signatures: (tool, method) pairs with parameter misalignment
    """

    missing_tools: list[str] = field(default_factory=list)
    orphaned_tools: list[str] = field(default_factory=list)
    mismatched_signatures: list[tuple[str, str]] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return bool(self.missing_tools or self.orphaned_tools or self.mismatched_signatures)

    @property
    def error_count(self) -> int:
        """Total number of errors found."""
        return len(self.missing_tools) + len(self.orphaned_tools) + len(self.mismatched_signatures)

    def __str__(self) -> str:
        """Format report for display."""
        lines = ["Coverage Report:"]

        if self.missing_tools:
            lines.append(
                f"  ❌ Methods without tools ({len(self.missing_tools)}): "
                f"{', '.join(self.missing_tools[:5])}"
                + ("..." if len(self.missing_tools) > 5 else "")
            )

        if self.orphaned_tools:
            lines.append(
                f"  ❌ Tools without methods ({len(self.orphaned_tools)}): "
                f"{', '.join(self.orphaned_tools[:5])}"
                + ("..." if len(self.orphaned_tools) > 5 else "")
            )

        if self.mismatched_signatures:
            lines.append(
                f"  ❌ Signature mismatches ({len(self.mismatched_signatures)}): "
                f"{', '.join([f'{t}↔{m}' for t, m in self.mismatched_signatures[:3]])}"
                + ("..." if len(self.mismatched_signatures) > 3 else "")
            )

        if not self.has_errors:
            lines.append("  ✅ All checks passed - 100% coverage")

        return "\n".join(lines)


@dataclass
class ConsistencyReport:
    """
    Internal registry consistency validation report.

    Validates registry integrity (duplicates, missing fields, versions).

    Attributes:
        issues: List of consistency issues found
    """

    issues: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return bool(self.issues)

    @property
    def error_count(self) -> int:
        """Total number of errors found."""
        return len(self.issues)

    def __str__(self) -> str:
        """Format report for display."""
        if not self.issues:
            return "Consistency Report: ✅ All checks passed"

        lines = ["Consistency Report:"]
        for issue in self.issues[:10]:  # Show first 10 issues
            lines.append(f"  ❌ {issue}")

        if len(self.issues) > 10:
            lines.append(f"  ... and {len(self.issues) - 10} more issues")

        return "\n".join(lines)


@dataclass
class DriftReport:
    """
    YAML-to-code drift detection report.

    Detects misalignment between YAML inventories and actual service code.

    Attributes:
        missing_in_yaml: Methods in code but not documented in YAML
        missing_in_code: Methods in YAML but not found in code
        signature_mismatches: Methods with signature drift
    """

    missing_in_yaml: set[str] = field(default_factory=set)
    missing_in_code: set[str] = field(default_factory=set)
    signature_mismatches: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return bool(self.missing_in_yaml or self.missing_in_code or self.signature_mismatches)

    @property
    def error_count(self) -> int:
        """Total number of errors found."""
        return (
            len(self.missing_in_yaml) + len(self.missing_in_code) + len(self.signature_mismatches)
        )

    def __str__(self) -> str:
        """Format report for display."""
        lines = ["Drift Report:"]

        if self.missing_in_yaml:
            yaml_list = sorted(self.missing_in_yaml)[:5]
            lines.append(
                f"  ⚠️  In code but not YAML ({len(self.missing_in_yaml)}): "
                f"{', '.join(yaml_list)}" + ("..." if len(self.missing_in_yaml) > 5 else "")
            )

        if self.missing_in_code:
            code_list = sorted(self.missing_in_code)[:5]
            lines.append(
                f"  ❌ In YAML but not code ({len(self.missing_in_code)}): "
                f"{', '.join(code_list)}" + ("..." if len(self.missing_in_code) > 5 else "")
            )

        if self.signature_mismatches:
            lines.append(
                f"  ❌ Signature mismatches ({len(self.signature_mismatches)}): "
                f"{', '.join(self.signature_mismatches[:5])}"
                + ("..." if len(self.signature_mismatches) > 5 else "")
            )

        if not self.has_errors:
            lines.append("  ✅ No drift detected")

        return "\n".join(lines)


@dataclass
class RegistryLoadResult:
    """
    Result of registry loading operation.

    Contains counts, validation reports, and success status.

    Attributes:
        success: Whether loading completed successfully
        methods_count: Number of methods loaded
        tools_count: Number of tools loaded
        coverage_report: Coverage validation results
        consistency_report: Consistency validation results
        drift_report: Drift detection results
        error: Error message if loading failed
    """

    success: bool = False
    methods_count: int = 0
    tools_count: int = 0
    coverage_report: CoverageReport | None = None
    consistency_report: ConsistencyReport | None = None
    drift_report: DriftReport | None = None
    error: str | None = None

    @property
    def has_errors(self) -> bool:
        """Check if any validation errors occurred."""
        return (
            not self.success
            or (self.coverage_report and self.coverage_report.has_errors)
            or (self.consistency_report and self.consistency_report.has_errors)
            or (self.drift_report and self.drift_report.has_errors)
        )

    @property
    def total_error_count(self) -> int:
        """Total number of validation errors across all reports."""
        count = 0
        if self.coverage_report:
            count += self.coverage_report.error_count
        if self.consistency_report:
            count += self.consistency_report.error_count
        if self.drift_report:
            count += self.drift_report.error_count
        return count

    def __str__(self) -> str:
        """Format result for display."""
        if not self.success:
            return f"❌ Registry Loading Failed: {self.error}"

        lines = [
            "Registry Loading Result:",
            f"  Methods: {self.methods_count}",
            f"  Tools: {self.tools_count}",
        ]

        if self.coverage_report:
            lines.append(f"\n{self.coverage_report}")

        if self.consistency_report:
            lines.append(f"\n{self.consistency_report}")

        if self.drift_report:
            lines.append(f"\n{self.drift_report}")

        if not self.has_errors:
            lines.append("\n✅ All validations passed")
        else:
            lines.append(f"\n⚠️  {self.total_error_count} total validation errors")

        return "\n".join(lines)


class RegistryValidationError(Exception):
    """
    Exception raised when registry validation fails in STRICT mode.

    Attributes:
        message: Error description
        report: Validation report with details
    """

    def __init__(self, message: str, report: object | None = None):
        """Initialize validation error."""
        self.message = message
        self.report = report
        super().__init__(message)

    def __str__(self) -> str:
        """Format error with report details."""
        if self.report:
            return f"{self.message}\n{self.report}"
        return self.message
