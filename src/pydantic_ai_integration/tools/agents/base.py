"""Stub agent runtime used during tool regeneration.

The historical codebase referenced ``tools.agents.base.default_agent`` when
registering tools. The actual agent runtime isn't part of this trimmed-down
repo, so we provide a minimal stand-in that matches the expected API surface
used by the generated code and tests.

Once a real agent implementation is available, this module can be replaced
with the concrete runtime. Until then the stub captures events on the
``MDSContext`` and returns deterministic results so unit tests can proceed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from ...dependencies import MDSContext


@dataclass
class AgentRuntime:
    """Minimal stand-in for the historical agent runtime."""

    name: str = "default"
    _tools: Dict[str, Callable[..., Awaitable[Any]]] = None

    def __post_init__(self) -> None:
        if self._tools is None:
            self._tools = {}

    def tool(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """Register a tool coroutine for later execution.

        The real runtime exposes a decorator-style API. The generated registry
        only calls this function for side effects, so we record the callable and
        return it unchanged to preserve decorator semantics.
        """

        name = getattr(func, "__name__", f"tool_{len(self._tools) + 1}")
        self._tools[name] = func
        return func

    async def run_tool(
        self,
        ctx: MDSContext,
        tool: Callable[..., Awaitable[Any]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a tool coroutine and return its result.

        This helper mimics the real runtime by calling the coroutine and
        emitting a success event on the context. Failures are propagated so
        existing error handling pathways (e.g. ToolResponse wrapping) can
        exercise their logic during tests.
        """

        result = await tool(ctx, **kwargs)
        ctx.register_event(
            "agent_runtime",
            {
                "tool": getattr(tool, "__name__", "<anonymous>"),
                "status": "success",
            },
        )
        return result


# Single shared instance matching the import expectations of generated code.
default_agent: AgentRuntime = AgentRuntime()
