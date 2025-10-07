"""
Simple import test to verify package structure works.
"""
import pytest


def test_casefile_service_import():
    """Test that CasefileService can be imported."""
    from casefileservice.service import CasefileService
    assert CasefileService is not None
    print("✓ CasefileService imported successfully")


def test_tool_session_service_import():
    """Test that ToolSessionService can be imported."""
    from tool_sessionservice.service import ToolSessionService
    assert ToolSessionService is not None
    print("✓ ToolSessionService imported successfully")


def test_pydantic_models_import():
    """Test that pydantic models can be imported."""
    from pydantic_models.operations.casefile_ops import CreateCasefileRequest
    assert CreateCasefileRequest is not None
    print("✓ Pydantic models imported successfully")