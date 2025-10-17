"""
Unit tests for RegistryLoader.

Tests registry loading, validation pipeline, and error handling.
"""

from unittest.mock import patch

from src.pydantic_ai_integration.registry.loader import (
    RegistryLoader,
    get_validation_mode_from_env,
)
from src.pydantic_ai_integration.registry.types import (
    ConsistencyReport,
    CoverageReport,
    DriftReport,
    RegistryLoadResult,
    RegistryValidationError,
    ValidationMode,
)


class TestRegistryLoader:
    """Test suite for RegistryLoader class."""

    def test_initialization_defaults(self):
        """Test loader initialization with default values."""
        loader = RegistryLoader()

        assert loader.validation_mode == ValidationMode.STRICT
        assert loader.enable_drift_detection is True

    def test_initialization_custom(self):
        """Test loader initialization with custom values."""
        loader = RegistryLoader(
            validation_mode=ValidationMode.WARNING, enable_drift_detection=False
        )

        assert loader.validation_mode == ValidationMode.WARNING
        assert loader.enable_drift_detection is False

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        return_value=10,
    )
    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_tools",
        return_value=10,
    )
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_coverage")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_consistency")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._detect_drift")
    def test_load_all_registries_success(
        self,
        mock_drift,
        mock_consistency,
        mock_coverage,
        mock_tools,
        mock_methods,
    ):
        """Test successful registry loading with all validations passing."""
        # Setup mocks to return successful reports
        mock_coverage.return_value = CoverageReport()
        mock_consistency.return_value = ConsistencyReport()
        mock_drift.return_value = DriftReport()

        loader = RegistryLoader()
        result = loader.load_all_registries()

        assert result.success
        assert result.methods_count == 10
        assert result.tools_count == 10
        assert not result.has_errors
        assert mock_methods.called
        assert mock_tools.called
        assert mock_coverage.called
        assert mock_consistency.called
        assert mock_drift.called

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        return_value=5,
    )
    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_tools",
        return_value=5,
    )
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_coverage")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_consistency")
    def test_load_without_drift_detection(
        self, mock_consistency, mock_coverage, mock_tools, mock_methods
    ):
        """Test loading with drift detection disabled."""
        mock_coverage.return_value = CoverageReport()
        mock_consistency.return_value = ConsistencyReport()

        loader = RegistryLoader(enable_drift_detection=False)
        result = loader.load_all_registries()

        assert result.success
        assert result.drift_report is None

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        return_value=10,
    )
    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_tools",
        return_value=8,
    )
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_coverage")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_consistency")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._detect_drift")
    def test_load_with_coverage_errors_strict(
        self,
        mock_drift,
        mock_consistency,
        mock_coverage,
        mock_tools,
        mock_methods,
    ):
        """Test loading with coverage errors in STRICT mode."""
        # Coverage validation finds missing tools
        mock_coverage.return_value = CoverageReport(missing_tools=["method1", "method2"])
        mock_consistency.return_value = ConsistencyReport()
        mock_drift.return_value = DriftReport()

        loader = RegistryLoader(validation_mode=ValidationMode.STRICT)

        # Should raise exception in STRICT mode
        try:
            loader.load_all_registries()
            raise AssertionError("Should have raised RegistryValidationError")
        except RegistryValidationError as e:
            assert "Coverage validation failed" in str(e)

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        return_value=10,
    )
    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_tools",
        return_value=8,
    )
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_coverage")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_consistency")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._detect_drift")
    def test_load_with_coverage_errors_warning(
        self,
        mock_drift,
        mock_consistency,
        mock_coverage,
        mock_tools,
        mock_methods,
    ):
        """Test loading with coverage errors in WARNING mode."""
        # Coverage validation finds missing tools
        mock_coverage.return_value = CoverageReport(missing_tools=["method1", "method2"])
        mock_consistency.return_value = ConsistencyReport()
        mock_drift.return_value = DriftReport()

        loader = RegistryLoader(validation_mode=ValidationMode.WARNING)
        result = loader.load_all_registries()

        # Should succeed but report has errors
        assert result.success
        assert result.has_errors
        assert result.coverage_report.has_errors

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        side_effect=Exception("Failed to load methods"),
    )
    def test_load_with_method_loading_failure_strict(self, mock_methods):
        """Test handling of method loading failure in STRICT mode."""
        loader = RegistryLoader(validation_mode=ValidationMode.STRICT)

        try:
            loader.load_all_registries()
            raise AssertionError("Should have raised exception")
        except Exception as e:
            assert "Failed to load methods" in str(e)

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        side_effect=Exception("Failed to load methods"),
    )
    def test_load_with_method_loading_failure_warning(self, mock_methods):
        """Test handling of method loading failure in WARNING mode."""
        loader = RegistryLoader(validation_mode=ValidationMode.WARNING)
        result = loader.load_all_registries()

        assert not result.success
        assert result.error is not None
        assert "Failed to load methods" in result.error

    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_methods",
        return_value=10,
    )
    @patch(
        "src.pydantic_ai_integration.registry.loader.RegistryLoader._load_tools",
        return_value=8,
    )
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_coverage")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._validate_consistency")
    @patch("src.pydantic_ai_integration.registry.loader.RegistryLoader._detect_drift")
    def test_load_with_drift_detection_enabled(
        self,
        mock_drift,
        mock_consistency,
        mock_coverage,
        mock_tools,
        mock_methods,
    ):
        """Test that drift detection is called when enabled."""
        mock_coverage.return_value = CoverageReport()
        mock_consistency.return_value = ConsistencyReport()
        mock_drift.return_value = DriftReport(
            missing_in_yaml={"ServiceA.method1"},
            missing_in_code=set(),
            signature_mismatches=[],
        )

        loader = RegistryLoader(validation_mode=ValidationMode.WARNING, enable_drift_detection=True)
        result = loader.load_all_registries()

        # Drift detection should be called
        mock_drift.assert_called_once()

        # Result should include drift report
        assert result.success
        assert result.drift_report is not None
        assert result.drift_report.has_errors
        assert "ServiceA.method1" in result.drift_report.missing_in_yaml


class TestValidationModeFromEnv:
    """Test suite for environment variable configuration."""

    @patch.dict("os.environ", {"REGISTRY_STRICT_VALIDATION": "true"})
    def test_env_strict_true(self):
        """Test STRICT mode from environment variable."""
        mode = get_validation_mode_from_env()
        assert mode == ValidationMode.STRICT

    @patch.dict("os.environ", {"REGISTRY_STRICT_VALIDATION": "false"})
    def test_env_strict_false(self):
        """Test WARNING mode from environment variable."""
        mode = get_validation_mode_from_env()
        assert mode == ValidationMode.WARNING

    @patch.dict("os.environ", {"REGISTRY_STRICT_VALIDATION": "TRUE"})
    def test_env_case_insensitive(self):
        """Test case-insensitive environment variable."""
        mode = get_validation_mode_from_env()
        assert mode == ValidationMode.STRICT

    @patch.dict("os.environ", {}, clear=True)
    def test_env_default(self):
        """Test default STRICT mode when env var not set."""
        mode = get_validation_mode_from_env()
        assert mode == ValidationMode.STRICT


class TestRegistryLoadResult:
    """Test suite for RegistryLoadResult type."""

    def test_success_result(self):
        """Test successful result with no errors."""
        result = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=10,
            coverage_report=CoverageReport(),
            consistency_report=ConsistencyReport(),
            drift_report=DriftReport(),
        )

        assert result.success
        assert not result.has_errors
        assert result.total_error_count == 0

    def test_result_with_coverage_errors(self):
        """Test result with coverage errors."""
        result = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
            coverage_report=CoverageReport(missing_tools=["m1", "m2"]),
            consistency_report=ConsistencyReport(),
        )

        assert result.success
        assert result.has_errors
        assert result.total_error_count == 2

    def test_result_with_multiple_error_types(self):
        """Test result with errors across multiple reports."""
        result = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
            coverage_report=CoverageReport(missing_tools=["m1"]),
            consistency_report=ConsistencyReport(issues=["i1", "i2"]),
            drift_report=DriftReport(missing_in_code={"m2", "m3"}),
        )

        assert result.has_errors
        assert result.total_error_count == 5  # 1 + 2 + 2

    def test_failed_result(self):
        """Test failed loading result."""
        result = RegistryLoadResult(success=False, error="Loading failed")

        assert not result.success
        assert result.has_errors
        assert result.error == "Loading failed"

    def test_result_str(self):
        """Test string representation of result."""
        result = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=10,
            coverage_report=CoverageReport(),
        )

        result_str = str(result)
        assert "Registry Loading Result" in result_str
        assert "Methods: 10" in result_str
        assert "Tools: 10" in result_str
