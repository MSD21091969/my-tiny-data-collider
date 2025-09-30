"""Centralized ID generation utilities for the MDS Objects platform."""

from __future__ import annotations

import re
import secrets
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable, Optional

from .config import get_environment

_DEFAULT_RANDOM_BYTES = 3  # 6 hex characters
_SANITIZE_PATTERN = re.compile(r"[^a-z0-9]")


def _sanitize_fragment(value: Optional[str], fallback: str, length: int) -> str:
    """Return a lowercase alphanumeric fragment derived from *value*."""
    if not value:
        return fallback
    cleaned = _SANITIZE_PATTERN.sub("", value.lower())
    if not cleaned:
        return fallback
    return (cleaned[-length:] if len(cleaned) > length else cleaned).ljust(length, "0")


def _random_token(num_bytes: int = _DEFAULT_RANDOM_BYTES) -> str:
    """Return a short, collision-resistant random token."""
    return secrets.token_hex(num_bytes)


@dataclass
class IDService:
    """Service responsible for generating customized identifiers."""

    environment: str
    random_token_factory: Callable[[int], str] = _random_token
    date_provider: Callable[[], datetime] = lambda: datetime.now(UTC)

    def _current_date_component(self) -> str:
        return self.date_provider().strftime("%y%m%d")

    def _build(self, prefix: str, *components: str) -> str:
        suffix = "_".join(filter(None, components))
        return f"{prefix}_{suffix}" if suffix else prefix

    def new_casefile_id(self) -> str:
        return self._build("cf", self._current_date_component(), self.random_token_factory())

    def new_tool_session_id(self, user_id: str, casefile_id: Optional[str]) -> str:
        user_fragment = _sanitize_fragment(user_id, fallback="user", length=4)
        case_fragment = _sanitize_fragment(casefile_id, fallback="none", length=4) if casefile_id else "none"
        return self._build(
            "ts",
            self._current_date_component(),
            f"{user_fragment}{case_fragment}",
            self.random_token_factory()
        )

    def new_chat_session_id(self, user_id: str, casefile_id: Optional[str]) -> str:
        user_fragment = _sanitize_fragment(user_id, fallback="user", length=4)
        case_fragment = _sanitize_fragment(casefile_id, fallback="none", length=4) if casefile_id else "none"
        return self._build(
            "cs",
            self._current_date_component(),
            f"{user_fragment}{case_fragment}",
            self.random_token_factory()
        )

    def new_session_request_id(self) -> str:
        return self._build("sr", self._current_date_component(), self.random_token_factory())

    def new_tool_event_id(self) -> str:
        return self._build("te", self._current_date_component(), self.random_token_factory())


_id_service_lock = threading.Lock()
_default_id_service: Optional[IDService] = None


def get_id_service() -> IDService:
    """Return the process-wide ID service instance."""
    global _default_id_service
    if _default_id_service is None:
        with _id_service_lock:
            if _default_id_service is None:
                _default_id_service = IDService(environment=get_environment())
    return _default_id_service


def set_id_service(service: IDService) -> None:
    """Override the global ID service (useful for tests)."""
    global _default_id_service
    with _id_service_lock:
        _default_id_service = service
