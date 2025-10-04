"""Agent runtime stubs used by generated tools.

This lightweight shim exists so auto-generated tool modules can
import ``default_agent`` without pulling in an unavailable runtime.
When the real agent subsystem is reintroduced, replace this package
with the actual implementation.
"""

from .base import default_agent, AgentRuntime

__all__ = ["default_agent", "AgentRuntime"]
