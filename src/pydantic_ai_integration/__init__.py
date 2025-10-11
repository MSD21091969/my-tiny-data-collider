"""
Pydantic AI integration module with unified registry loading.

Provides:
- Unified registry loader with validation and drift detection
- Tool and method registration from YAML and decorators
- Comprehensive validation reporting
"""

__version__ = "0.1.0"

import logging
import os

# Import tools to trigger @register_mds_tool decorator execution
from . import tools  # noqa: F401

# Import registry components
from .registry import RegistryLoader, ValidationMode

logger = logging.getLogger(__name__)


def initialize_registries(
    validation_mode: ValidationMode = None,
    enable_drift_detection: bool = True,
) -> bool:
    """
    Initialize method and tool registries using unified loader.

    This function replaces the previous separate registration calls with
    a unified, validated loading approach.

    Args:
        validation_mode: Validation strictness (None = auto from env)
        enable_drift_detection: Enable YAML-to-code drift detection

    Returns:
        True if loading succeeded, False otherwise

    Environment Variables:
        REGISTRY_STRICT_VALIDATION: Set to 'true' for STRICT mode

    Example:
        >>> # In main.py or application startup
        >>> from src.pydantic_ai_integration import initialize_registries
        >>> if not initialize_registries():
        ...     logger.error("Failed to initialize registries")
    """
    # Auto-detect validation mode from environment if not specified
    if validation_mode is None:
        strict_env = os.getenv("REGISTRY_STRICT_VALIDATION", "false").lower()
        validation_mode = ValidationMode.STRICT if strict_env == "true" else ValidationMode.WARNING

    try:
        # Create loader with configuration
        loader = RegistryLoader(
            validation_mode=validation_mode,
            enable_drift_detection=enable_drift_detection,
        )

        # Load all registries with validation
        result = loader.load_all_registries()

        if result.success:
            logger.info(
                f"✅ Registries initialized: {result.methods_count} methods, "
                f"{result.tools_count} tools"
            )

            # Log validation results
            if result.coverage_report and result.coverage_report.has_errors:
                logger.warning(f"Coverage issues: {result.coverage_report}")

            if result.consistency_report and result.consistency_report.has_errors:
                logger.warning(f"Consistency issues: {result.consistency_report}")

            if result.drift_report and result.drift_report.has_errors:
                logger.warning(f"Drift detected: {result.drift_report}")

            return True
        else:
            logger.error(f"❌ Registry loading failed: {result.error}")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to initialize registries: {e}", exc_info=True)
        return False


# Auto-initialize on import (backward compatibility)
# Can be disabled by setting SKIP_AUTO_INIT=true
if os.getenv("SKIP_AUTO_INIT", "false").lower() != "true":
    try:
        initialize_registries()
    except Exception as e:
        logger.warning(
            f"Auto-initialization failed: {e}. Call initialize_registries() explicitly if needed."
        )
