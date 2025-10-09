"""Coreservice public API surface."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

from .config import get_config, get_environment
from .policy_patterns import PolicyPatternLoader

__all__ = [
	"get_config",
	"get_environment",
	"PolicyPatternLoader",
	"RequestHub",
	"execute_casefile",
	"execute_casefile_with_session",
]

if TYPE_CHECKING:  # pragma: no cover - type only import to avoid cycles at runtime
	from .request_hub import RequestHub, execute_casefile, execute_casefile_with_session


def __getattr__(name: str) -> Any:
	"""Lazily import RequestHub helpers to avoid circular imports."""
	if name in {"RequestHub", "execute_casefile", "execute_casefile_with_session"}:
		module = import_module(".request_hub", __name__)
		return getattr(module, name)
	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")