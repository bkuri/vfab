"""
Status commands for ploTTY.

This module provides status and monitoring commands for checking system status,
job queue, and individual job information without needing to launch full dashboard.
"""

from __future__ import annotations

import typer

from .system import show_status_overview, show_system_status, show_quick_status
from .queue import show_job_queue
from .job import show_job_details
from .session import session_reset, session_info
from .utils import complete_job_id

# Create status command group
status_app = typer.Typer(
    help="Status and monitoring commands", invoke_without_command=True
)


@status_app.callback()
def status_callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show complete status overview or run subcommands."""
    if ctx.invoked_subcommand is None:
        # Show complete status overview when no subcommand is provided
        show_status_overview(json_output=json_output, csv_output=csv_output)


@status_app.command("system")
def status_system(
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show overall system status."""
    show_system_status(json_output=json_output, csv_output=csv_output)


@status_app.command("tldr")
def status_tldr(
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show quick overview of system and queue (too long; didn't read)."""
    show_quick_status(json_output=json_output, csv_output=csv_output)


@status_app.command("queue")
def status_queue(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of jobs to show"
    ),
    state: str = typer.Option(None, "--state", "-s", help="Filter by job state"),
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show jobs in queue."""
    show_job_queue(
        limit=limit,
        state=state,
        json_output=json_output,
        csv_output=csv_output,
    )


@status_app.command("job")
def status_job(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to show details for"
    ),
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export status as CSV"),
):
    """Show detailed information about a specific job."""
    show_job_details(job_id, json_output=json_output, csv_output=csv_output)


@status_app.command("reset")
def status_reset():
    """Reset the current session (clear all jobs and layers)."""
    session_reset()


@status_app.command("session")
def status_session():
    """Show current session information."""
    session_info()


__all__ = ["status_app"]
