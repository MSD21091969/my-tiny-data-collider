"""Policy pattern loader for RequestHub orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class PolicyPattern:
    """Represents a reusable orchestration policy template."""

    name: str
    description: str
    defaults: Dict[str, Any]


class PolicyPatternLoader:
    """Loads policy patterns for RequestHub orchestration.

    In future iterations this loader can fetch patterns from YAML or a registry.
    For the MVP we keep a small in-memory catalog that the RequestHub can merge
    with per-request policy hints.
    """

    def __init__(self) -> None:
        self._patterns: Dict[str, PolicyPattern] = {
            "default": PolicyPattern(
                name="default",
                description="Standard request hub policy with auth + metrics hooks.",
                defaults={
                    "require_auth": True,
                    "emit_metrics": True,
                    "audit": True,
                },
            ),
            "tool_session_observer": PolicyPattern(
                name="tool_session_observer",
                description="Ensures tool session context is loaded and hooks fire for monitoring.",
                defaults={
                    "context_requirements": ["session"],
                    "hooks": ["metrics", "audit"],
                },
            ),
        }

    def load(self, name: str | None) -> Dict[str, Any]:
        """Load a policy by name, returning fallback defaults when not found."""
        if not name:
            return self._patterns["default"].defaults.copy()

        pattern = self._patterns.get(name)
        if not pattern:
            return self._patterns["default"].defaults.copy()
        return pattern.defaults.copy()
