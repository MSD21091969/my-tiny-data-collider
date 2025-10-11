"""
Registry module - Unified loading, validation, and drift detection.

This module consolidates method and tool registry loading with comprehensive
validation and drift detection capabilities.

Key Components:
    - RegistryLoader: Unified loading with transactional semantics
    - Validators: Coverage, consistency, and drift detection
    - Types: Shared types and validation modes

Usage:
    from pydantic_ai_integration.registry import RegistryLoader, ValidationMode

    loader = RegistryLoader(validation_mode=ValidationMode.STRICT)
    result = loader.load_all_registries()
"""

from .types import (
    ValidationMode,
    RegistryLoadResult,
    CoverageReport,
    ConsistencyReport,
    DriftReport,
)
from .loader import RegistryLoader

__all__ = [
    "RegistryLoader",
    "ValidationMode",
    "RegistryLoadResult",
    "CoverageReport",
    "ConsistencyReport",
    "DriftReport",
]
