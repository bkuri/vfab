"""
CLI package for ploTTY.

This package contains the main CLI interface split into logical command groups.
"""

from __future__ import annotations

import typer
from importlib import metadata

from .add import add_app
from .remove import remove_app
from .list import list_app
from .device import device_app
from .sos import sos_app
from .stats import stats_app
from .batch import batch_app
from .logs import logs_app
from .backup import backup_app

# Import check and info commands
from .check import check_app
from .info import status_app

# Import main level commands
from .list.setup_wizard import setup, check_config
from .interactive import interactive_command
from .job_commands import start_command, plan_command, record_test_command

# Get version
try:
    __version__ = metadata.version("plotty")
except metadata.PackageNotFoundError:
    __version__ = "1.2.0"

# Create main app
app = typer.Typer(no_args_is_help=True)

# Add main level commands
app.command("setup", help="Run setup wizard")(setup)
app.command("check-config", help="Check configuration")(check_config)
app.command("interactive", help="Start interactive plotting session")(
    interactive_command
)
app.command("start", help="Start plotting a job")(start_command)
app.command("prepare", help="Prepare a job for plotting")(plan_command)
app.command("record-test", help="Record a test plot for timing")(record_test_command)

# Add sub-apps (alphabetical order)
app.add_typer(add_app, name="add", help="Add new resources")
app.add_typer(backup_app, name="backup", help="Backup and restore commands")
app.add_typer(batch_app, name="batch", help="Batch operations commands")
app.add_typer(check_app, name="check", help="System and device checking")
app.add_typer(device_app, name="device", help="Device management commands")
app.add_typer(list_app, name="list", help="List and manage resources")
app.add_typer(logs_app, name="logs", help="Logging system commands")
app.add_typer(remove_app, name="remove", help="Remove resources")
app.add_typer(sos_app, name="sos", help="Recovery and rescue commands")
app.add_typer(stats_app, name="stats", help="Statistics and analytics commands")
app.add_typer(status_app, name="info", help="Status and monitoring commands")


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
