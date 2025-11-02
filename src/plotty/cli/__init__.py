"""
CLI package for ploTTY.

This package contains the main CLI interface split into logical command groups.
"""

from __future__ import annotations

import typer

from .plot import plot_app
from .job import job_app
from .config import config_app
from .recovery import recovery_app
from .guard import guard_app
from .stats import stats_app
from .batch import batch_app
from .logging import logging_app
from .backup import backup_app

# Import status commands from parent module
from ..cli_status import status_app

# Create main app
app = typer.Typer(no_args_is_help=False, invoke_without_command=True)

# Add sub-apps
app.add_typer(status_app, name="status", help="Status and monitoring commands")
app.add_typer(plot_app, name="plot", help="Plotting commands")
app.add_typer(job_app, name="job", help="Job management commands")
app.add_typer(config_app, name="config", help="Configuration commands")
app.add_typer(recovery_app, name="recovery", help="Crash recovery commands")
app.add_typer(guard_app, name="guard", help="System guard commands")
app.add_typer(stats_app, name="stats", help="Statistics and analytics commands")
app.add_typer(batch_app, name="batch", help="Batch operations commands")
app.add_typer(logging_app, name="logging", help="Logging system commands")
app.add_typer(backup_app, name="backup", help="Backup and restore commands")


@app.callback()
def main_callback():
    """ploTTY - Plotter management system."""
    pass


if __name__ == "__main__":
    app()
