"""Compatibility module exposing tool session models.

Older integration tests import `src.pydantic_models.tool_session` directly.
The canonical definitions now live under `pydantic_models.operations.tool_execution_ops`.
This shim re-exports the public classes so legacy imports continue to work.
"""
from .operations.tool_execution_ops import (
    ToolRequest,
    ToolRequestPayload,
    ToolResponse,
)

__all__ = ["ToolRequest", "ToolRequestPayload", "ToolResponse"]
