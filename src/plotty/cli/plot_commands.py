"""
Plotting commands for ploTTY CLI.
"""

from __future__ import annotations

from typing import Optional
import typer

from ..utils import error_handler
from .core import get_available_job_ids

# Create plot command group
plot_app = typer.Typer(help="Plotting commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@plot_app.command()
def plot(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plot"
    ),
):
    """Plot a job."""
    try:
        # This will be implemented with the actual plotting logic
        print(f"Plotting job: {job_id}")
        # TODO: Implement actual plotting functionality
    except Exception as e:
        error_handler.handle(e)


@plot_app.command()
def interactive(port: Optional[str] = None, model: int = 1, units: str = "inches"):
    """Start interactive plotting session."""
    try:
        # TODO: Implement interactive plotting
        print(
            f"Starting interactive session on port {port}, model {model}, units {units}"
        )
    except Exception as e:
        error_handler.handle(e)


@plot_app.command()
def pen_test(port: Optional[str] = None, model: int = 1, cycles: int = 3):
    """Test pen operation."""
    try:
        # TODO: Implement pen test
        print(f"Running pen test: {cycles} cycles on port {port}, model {model}")
    except Exception as e:
        error_handler.handle(e)
