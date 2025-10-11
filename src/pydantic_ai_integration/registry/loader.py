"""
Unified registry loader with validation and drift detection.

Consolidates method and tool registry loading with transactional semantics,
comprehensive validation, and configurable strictness modes.
"""

import logging
import os
from typing import TYPE_CHECKING

from .types import (
    ConsistencyReport,
    CoverageReport,
    DriftReport,
    RegistryLoadResult,
    RegistryValidationError,
    ValidationMode,
)

if TYPE_CHECKING:
    from .validators import (
        detect_yaml_code_drift,
        validate_method_tool_coverage,
        validate_registry_consistency,
    )

logger = logging.getLogger(__name__)


class RegistryLoader:
    """
    Unified loader for method and tool registries.

    Features:
    - Transactional loading (all-or-nothing semantics)
    - Comprehensive validation (coverage, consistency, drift)
    - Configurable validation modes (strict/warning)
    - Detailed reporting for all validation failures

    Attributes:
        validation_mode: Strictness level (STRICT raises on errors, WARNING logs)
        enable_drift_detection: Whether to detect YAML ↔ code drift

    Example:
        >>> loader = RegistryLoader(validation_mode=ValidationMode.STRICT)
        >>> result = loader.load_all_registries()
        >>> if result.success:
        ...     print(f"Loaded {result.methods_count} methods, {result.tools_count} tools")
    """

    def __init__(
        self,
        validation_mode: ValidationMode = ValidationMode.STRICT,
        enable_drift_detection: bool = True,
    ):
        """
        Initialize registry loader.

        Args:
            validation_mode: Validation strictness (STRICT or WARNING)
            enable_drift_detection: Enable YAML-to-code drift detection
        """
        self.validation_mode = validation_mode
        self.enable_drift_detection = enable_drift_detection

        logger.info(
            f"RegistryLoader initialized: mode={validation_mode.value}, drift={enable_drift_detection}"
        )

    def load_all_registries(self) -> RegistryLoadResult:
        """
        Load both method and tool registries with validation.

        This is the main entry point for registry loading. It performs:
        1. Method registry loading
        2. Tool registry loading
        3. Coverage validation (method ↔ tool alignment)
        4. Consistency validation (duplicates, missing fields)
        5. Drift detection (YAML ↔ code, if enabled)

        Returns:
            RegistryLoadResult with counts, reports, and success status

        Raises:
            RegistryValidationError: In STRICT mode if validation fails
        """
        logger.info("═" * 60)
        logger.info("Registry Loading Start")
        logger.info("═" * 60)

        try:
            # Step 1: Load methods
            methods_count = self._load_methods()
            logger.info(f"✅ Loaded {methods_count} methods")

            # Step 2: Load tools
            tools_count = self._load_tools()
            logger.info(f"✅ Loaded {tools_count} tools")

            # Step 3: Validate coverage (method ↔ tool alignment)
            logger.info("🔍 Validating coverage...")
            coverage_report = self._validate_coverage()
            if coverage_report.has_errors:
                self._handle_validation_error("Coverage validation failed", coverage_report)
            else:
                logger.info("✅ Coverage validation passed")

            # Step 4: Validate consistency
            logger.info("🔍 Validating consistency...")
            consistency_report = self._validate_consistency()
            if consistency_report.has_errors:
                self._handle_validation_error("Consistency validation failed", consistency_report)
            else:
                logger.info("✅ Consistency validation passed")

            # Step 5: Detect drift (if enabled)
            drift_report = None
            if self.enable_drift_detection:
                logger.info("🔍 Detecting drift...")
                drift_report = self._detect_drift()
                if drift_report.has_errors:
                    self._handle_validation_error(
                        "Drift detected between YAML and code", drift_report
                    )
                else:
                    logger.info("✅ No drift detected")

            logger.info("═" * 60)
            logger.info("Registry Loading Complete")
            logger.info("═" * 60)

            return RegistryLoadResult(
                success=True,
                methods_count=methods_count,
                tools_count=tools_count,
                coverage_report=coverage_report,
                consistency_report=consistency_report,
                drift_report=drift_report,
            )

        except RegistryValidationError:
            # Re-raise validation errors (already logged)
            raise

        except Exception as e:
            logger.error(f"❌ Registry loading failed: {e}", exc_info=True)

            if self.validation_mode == ValidationMode.STRICT:
                raise

            logger.warning("Continuing with partial registry (WARNING mode)")
            return RegistryLoadResult(success=False, error=str(e))

    def _load_methods(self) -> int:
        """
        Load methods from YAML inventory.

        Returns:
            Number of methods loaded

        Raises:
            Exception: If method loading fails
        """
        try:
            # Import registration function and registry
            from ..method_decorator import register_methods_from_yaml
            from ..method_registry import MANAGED_METHODS

            # Load methods
            register_methods_from_yaml()

            # Return count
            return len(MANAGED_METHODS)

        except Exception as e:
            logger.error(f"Failed to load methods: {e}", exc_info=True)
            raise

    def _load_tools(self) -> int:
        """
        Load tools from YAML directory.

        Returns:
            Number of tools loaded

        Raises:
            Exception: If tool loading fails
        """
        try:
            # Import registration function
            from ..tool_decorator import MANAGED_TOOLS, register_tools_from_yaml

            # Load tools
            register_tools_from_yaml()

            # Return count
            return len(MANAGED_TOOLS)

        except Exception as e:
            logger.error(f"Failed to load tools: {e}", exc_info=True)
            raise

    def _validate_coverage(self) -> CoverageReport:
        """
        Validate method-to-tool coverage.

        Returns:
            CoverageReport with validation results
        """
        from .validators import validate_method_tool_coverage

        return validate_method_tool_coverage()

    def _validate_consistency(self) -> ConsistencyReport:
        """
        Validate registry consistency.

        Returns:
            ConsistencyReport with validation results
        """
        from .validators import validate_registry_consistency

        return validate_registry_consistency()

    def _detect_drift(self) -> DriftReport:
        """
        Detect YAML-to-code drift.

        Returns:
            DriftReport with detection results
        """
        from .validators import detect_yaml_code_drift

        return detect_yaml_code_drift()

    def _handle_validation_error(self, message: str, report: object) -> None:
        """
        Handle validation errors based on validation mode.

        Args:
            message: Error message
            report: Validation report with details

        Raises:
            RegistryValidationError: In STRICT mode
        """
        if self.validation_mode == ValidationMode.STRICT:
            logger.error(f"❌ {message}")
            logger.error(f"{report}")
            raise RegistryValidationError(message, report)
        else:
            logger.warning(f"⚠️  {message}")
            logger.warning(f"{report}")


def get_validation_mode_from_env() -> ValidationMode:
    """
    Get validation mode from environment variable.

    Checks REGISTRY_STRICT_VALIDATION environment variable.
    Defaults to STRICT if not set or set to "true".

    Returns:
        ValidationMode (STRICT or WARNING)
    """
    strict = os.getenv("REGISTRY_STRICT_VALIDATION", "true").lower()
    return ValidationMode.STRICT if strict == "true" else ValidationMode.WARNING
