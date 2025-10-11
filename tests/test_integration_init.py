"""
Integration tests for pydantic_ai_integration initialization.

Tests the new initialize_registries() function and auto-initialization.
"""

import os
from unittest.mock import MagicMock, patch

from src.pydantic_ai_integration import initialize_registries
from src.pydantic_ai_integration.registry import RegistryLoadResult, ValidationMode


class TestInitializeRegistries:
    """Test suite for initialize_registries function."""

    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_with_default_mode(self, mock_loader_class):
        """Test initialization with default validation mode."""
        # Setup mock
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
        )

        # Call with defaults
        result = initialize_registries()

        # Should succeed
        assert result is True
        mock_loader_class.assert_called_once()
        mock_loader.load_all_registries.assert_called_once()

    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_with_strict_mode(self, mock_loader_class):
        """Test initialization with STRICT validation mode."""
        # Setup mock
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
        )

        # Call with STRICT mode
        result = initialize_registries(validation_mode=ValidationMode.STRICT)

        # Should create loader with STRICT mode
        assert result is True
        mock_loader_class.assert_called_once_with(
            validation_mode=ValidationMode.STRICT,
            enable_drift_detection=True,
        )

    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_with_drift_disabled(self, mock_loader_class):
        """Test initialization with drift detection disabled."""
        # Setup mock
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
        )

        # Call with drift detection disabled
        result = initialize_registries(enable_drift_detection=False)

        # Should create loader with drift detection disabled
        assert result is True
        mock_loader_class.assert_called_once()
        call_kwargs = mock_loader_class.call_args[1]
        assert call_kwargs["enable_drift_detection"] is False

    @patch.dict(os.environ, {"REGISTRY_STRICT_VALIDATION": "true"})
    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_from_env_strict(self, mock_loader_class):
        """Test initialization reads STRICT mode from environment."""
        # Setup mock
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
        )

        # Call without explicit mode (should read from env)
        result = initialize_registries()

        # Should use STRICT mode from environment
        assert result is True
        call_kwargs = mock_loader_class.call_args[1]
        assert call_kwargs["validation_mode"] == ValidationMode.STRICT

    @patch.dict(os.environ, {"REGISTRY_STRICT_VALIDATION": "false"})
    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_from_env_warning(self, mock_loader_class):
        """Test initialization reads WARNING mode from environment."""
        # Setup mock
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=True,
            methods_count=10,
            tools_count=8,
        )

        # Call without explicit mode (should read from env)
        result = initialize_registries()

        # Should use WARNING mode from environment
        assert result is True
        call_kwargs = mock_loader_class.call_args[1]
        assert call_kwargs["validation_mode"] == ValidationMode.WARNING

    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_failure(self, mock_loader_class):
        """Test initialization handles failures gracefully."""
        # Setup mock to fail
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_all_registries.return_value = RegistryLoadResult(
            success=False,
            error="Failed to load",
        )

        # Call should return False
        result = initialize_registries()

        assert result is False

    @patch("src.pydantic_ai_integration.RegistryLoader")
    def test_initialize_exception(self, mock_loader_class):
        """Test initialization handles exceptions gracefully."""
        # Setup mock to raise exception
        mock_loader_class.side_effect = Exception("Loader failed")

        # Call should return False (not raise)
        result = initialize_registries()

        assert result is False


class TestBackwardCompatibility:
    """Test backward compatibility with old initialization approach."""

    def test_can_still_import_registration_functions(self):
        """Test that old registration functions are still importable."""
        # These imports should still work for backward compatibility
        from src.pydantic_ai_integration.method_decorator import (
            register_methods_from_yaml,
        )
        from src.pydantic_ai_integration.tool_decorator import (
            register_tools_from_yaml,
        )

        assert callable(register_methods_from_yaml)
        assert callable(register_tools_from_yaml)

    def test_registries_accessible(self):
        """Test that registries are still directly accessible."""
        from src.pydantic_ai_integration.method_registry import MANAGED_METHODS
        from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS

        assert isinstance(MANAGED_METHODS, dict)
        assert isinstance(MANAGED_TOOLS, dict)
