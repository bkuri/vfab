"""
Statistics commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

from .summary import show_summary
from .jobs import show_job_stats
from .performance import show_performance

# Create stats command group
stats_app = typer.Typer(help="Statistics and analytics commands")

# Register commands
stats_app.command("summary")(show_summary)
stats_app.command("jobs")(show_job_stats)
stats_app.command("performance")(show_performance)

__all__ = ["stats_app"]
