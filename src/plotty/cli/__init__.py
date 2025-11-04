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

# Import check and info commands
from .check import check_app
from .info import status_app

# Import system command group
from .system import system_app

# Import main level commands
from .list.setup_wizard import setup
from .interactive import interactive_command
from .job_commands import start_command, optimize_command
from .resume import resume_command
from .restart import restart_command

# Get version
try:
    __version__ = metadata.version("plotty")
except metadata.PackageNotFoundError:
    __version__ = "1.2.0"

# Create main app
app = typer.Typer(no_args_is_help=True)

# Add main level commands
app.command("setup", help="Run setup wizard")(setup)
app.command("interactive", help="Start interactive plotting session")(
    interactive_command
)
app.command("start", help="Begin plotting a job")(start_command)
app.command("optimize", help="Optimize jobs for plotting")(optimize_command)
app.command("resume", help="Resume interrupted plotting jobs")(resume_command)
app.command("restart", help="Restart job from beginning")(restart_command)

# Add sub-apps (alphabetical order)
app.add_typer(add_app, name="add", help="Add new resources")
app.add_typer(check_app, name="check", help="System and device checking")
app.add_typer(list_app, name="list", help="List and manage resources")
app.add_typer(remove_app, name="remove", help="Remove resources")
app.add_typer(system_app, name="system", help="System management commands")
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
