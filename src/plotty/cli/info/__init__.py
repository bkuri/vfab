"""
Info commands for ploTTY.

This module provides information and monitoring commands for checking system status,
job queue, and individual job information without needing to launch full dashboard.
"""

from __future__ import annotations

import typer

from .system import show_status_overview, show_system_status, show_quick_status
from .job import show_job_details
from .session import session_reset, session_info
from .queue import show_job_queue
from .utils import complete_job_id
from .paths import paths_command

# Create info command group
info_app = typer.Typer(
    help="Information and monitoring commands", invoke_without_command=True
)


@info_app.callback()
def info_callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show complete status overview or run subcommands."""
    if ctx.invoked_subcommand is None:
        # Show complete status overview when no subcommand is provided
        show_status_overview(json_output=json_output, csv_output=csv_output)


@info_app.command("system")
def info_system(
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show overall system status."""
    show_system_status(json_output=json_output, csv_output=csv_output)


@info_app.command("tldr")
def info_tldr(
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show quick overview of system and queue (too long; didn't read)."""
    show_quick_status(json_output=json_output, csv_output=csv_output)


@info_app.command("job")
def info_job(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to show details for"
    ),
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show detailed information about a specific job."""
    show_job_details(job_id, json_output=json_output, csv_output=csv_output)


@info_app.command("reset")
def info_reset(
    apply: bool = typer.Option(
        False, "--apply", help="Apply session reset (dry-run by default)"
    ),
):
    """Reset the current session (clear all jobs and layers)."""
    session_reset(apply=apply)


@info_app.command("session")
def info_session():
    """Show current session information."""
    session_info()


@info_app.command("queue")
def info_queue(
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of jobs shown"),
    state: str = typer.Option(None, "--state", "-s", help="Filter by job state"),
    json_output: bool = typer.Option(False, "--json", help="Export as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export as CSV"),
):
    """Show job queue status."""
    show_job_queue(
        limit=limit, state=state, json_output=json_output, csv_output=csv_output
    )


@info_app.command("paths")
def info_paths():
    """Show ploTTY file paths and configuration locations."""
    paths_command()


__all__ = ["info_app"]
