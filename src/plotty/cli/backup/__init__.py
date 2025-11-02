"""
Backup and restore commands for ploTTY.

Provides CLI interface for creating, managing, and restoring backups
of configurations, jobs, workspace data, and application state.
"""

from __future__ import annotations

import typer

from .create import create_app
from .list import list_app
from .restore import restore_app
from .delete import delete_app
from .info import info_app
from .cleanup import cleanup_app

# Create main backup app
backup_app = typer.Typer(
    name="backup", help="Backup and restore operations", no_args_is_help=True
)

# Add sub-apps
backup_app.add_typer(create_app, name="create", help="Create a backup")
backup_app.add_typer(list_app, name="list", help="List available backups")
backup_app.add_typer(restore_app, name="restore", help="Restore from backup")
backup_app.add_typer(delete_app, name="delete", help="Delete a backup")
backup_app.add_typer(info_app, name="info", help="Show backup information")
backup_app.add_typer(cleanup_app, name="cleanup", help="Clean up old backups")
