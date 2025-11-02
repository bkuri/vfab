"""
Status and monitoring commands for ploTTY.

This module provides commands for checking system status,
job queue, and individual job information.
"""

from .status import status_app

__all__ = ["status_app"]
