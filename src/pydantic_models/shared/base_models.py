"""Compatibility module exposing shared base models.

The legacy integration tests import RequestStatus from
``src.pydantic_models.shared.base_models``. The project recently
consolidated the enum into ``src.pydantic_models.base.types``. This module
bridges the gap without forcing changes to generated tests.
"""

from __future__ import annotations

from src.pydantic_models.base.types import RequestStatus

__all__ = ["RequestStatus"]
