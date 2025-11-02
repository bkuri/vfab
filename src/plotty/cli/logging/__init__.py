"""
Logging management commands for ploTTY.

Provides commands for viewing, configuring, and managing the ploTTY
logging system including log files, levels, and monitoring.
"""

from __future__ import annotations

import typer

from .status import logging_status
from .view import view_logs
from .configure import configure_logging
from .test import test_logging
from .cleanup import cleanup_logs

# Create CLI app
logging_app = typer.Typer(
    name="logging",
    help="Logging system management and monitoring",
    no_args_is_help=True,
)

# Register commands
logging_app.command("status")(logging_status)
logging_app.command("view")(view_logs)
logging_app.command("configure")(configure_logging)
logging_app.command("test")(test_logging)
logging_app.command("cleanup")(cleanup_logs)

__all__ = ["logging_app"]
