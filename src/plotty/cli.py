"""
Main CLI entry point - redirects to new CLI package structure.

This maintains backward compatibility while using the new modular CLI structure.
"""

from __future__ import annotations

from .cli import app

# Export the main app for backward compatibility
__all__ = ["app"]
