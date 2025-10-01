"""
Coreservice initialization.
"""

from .config import get_environment as get_environment, get_config as get_config

__all__ = ["get_environment", "get_config"]