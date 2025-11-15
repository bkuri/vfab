"""
System management commands for vfab CLI.

This module provides system-level operations including logging,
statistics, backup/restore, and recovery functions.
"""

from __future__ import annotations

import typer

from .export import export_command
from .import_cmd import import_command
from .logs import logs_app
from .stats import stats_app

# Create system command group
system_app = typer.Typer(no_args_is_help=True, help="System management commands")

# Add commands and sub-apps (alphabetical order)
system_app.command("export", help="Export and backup operations")(export_command)
system_app.command("import", help="Import and restore operations")(import_command)
system_app.add_typer(logs_app, name="logs", help="Log management commands")
system_app.add_typer(stats_app, name="stats", help="Statistics and analytics")

__all__ = ["system_app"]
