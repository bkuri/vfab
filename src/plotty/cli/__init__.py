"""
CLI package for ploTTY.

This package contains the main CLI interface split into logical command groups.
"""

from __future__ import annotations

import typer
from importlib import metadata

from .job import job_app
from .config import config_app
from .device import device_app
from .recovery import recovery_app
from .guard import guard_app
from .stats import stats_app
from .batch import batch_app
from .logging import logging_app
from .backup import backup_app

# Import status commands
from .status import status_app

# Get version
try:
    __version__ = metadata.version("plotty")
except metadata.PackageNotFoundError:
    __version__ = "1.2.0"

# Create main app
app = typer.Typer(no_args_is_help=True)

# Add sub-apps
app.add_typer(status_app, name="status", help="Status and monitoring commands")
app.add_typer(job_app, name="job", help="Job management commands")
app.add_typer(config_app, name="config", help="Configuration commands")
app.add_typer(device_app, name="device", help="Device management commands")
app.add_typer(recovery_app, name="recovery", help="Crash recovery commands")
app.add_typer(guard_app, name="guard", help="System guard commands")
app.add_typer(stats_app, name="stats", help="Statistics and analytics commands")
app.add_typer(batch_app, name="batch", help="Batch operations commands")
app.add_typer(logging_app, name="logging", help="Logging system commands")
app.add_typer(backup_app, name="backup", help="Backup and restore commands")


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
):
    """ploTTY - Plotter management system."""
    if version:
        typer.echo(f"ploTTY v{__version__}")
        raise typer.Exit()


def main():
    """Main entry point for plotty CLI."""
    app()


if __name__ == "__main__":
    main()
