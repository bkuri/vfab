"""
Statistics commands for ploTTY.

This module provides commands for viewing and analyzing plotting statistics,
including job performance, layer metrics, and system analytics.
"""

from __future__ import annotations

import typer

from .summary import show_stats_summary
from .jobs import show_job_stats
from .performance import show_performance_stats

# Create stats command group
stats_app = typer.Typer(
    help="Statistics and analytics commands", invoke_without_command=True
)


@stats_app.callback()
def stats_callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Export stats as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export stats as CSV"),
):
    """Show statistics overview or run subcommands."""
    if ctx.invoked_subcommand is None:
        # Show statistics summary when no subcommand is provided
        show_stats_summary(json_output=json_output, csv_output=csv_output)


@stats_app.command("summary")
def stats_summary(
    json_output: bool = typer.Option(False, "--json", help="Export stats as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export stats as CSV"),
):
    """Show overall statistics summary."""
    show_stats_summary(json_output=json_output, csv_output=csv_output)


@stats_app.command("jobs")
def stats_jobs(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of jobs to show"
    ),
    json_output: bool = typer.Option(False, "--json", help="Export stats as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export stats as CSV"),
):
    """Show job-related statistics."""
    show_job_stats(limit=limit, json_output=json_output, csv_output=csv_output)


@stats_app.command("performance")
def stats_performance(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
    json_output: bool = typer.Option(False, "--json", help="Export stats as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Export stats as CSV"),
):
    """Show performance metrics and trends."""
    show_performance_stats(days=days, json_output=json_output, csv_output=csv_output)


__all__ = ["stats_app"]
