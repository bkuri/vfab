"""
Device management commands for ploTTY CLI.

This module provides commands for device testing and interactive plotting sessions.
"""

from __future__ import annotations

import typer

from .test import test_device
from .interactive import interactive_session

# Create device command group
device_app = typer.Typer(no_args_is_help=True, help="Device management commands")

# Register commands
device_app.command("test", help="Test device operation")(test_device)
device_app.command("interactive", help="Start interactive plotting session")(
    interactive_session
)

__all__ = ["device_app"]
