"""
API package initialization.
"""

from .app import app as app, create_app as create_app

__all__ = ["app", "create_app"]