"""
Job management commands for ploTTY CLI.

Provides CLI interface for managing plotting jobs including:
- Adding new jobs from SVG files
- Planning jobs for plotting with pen assignments
- Listing and viewing job status
- Removing jobs from workspace
- Recording test plots for timing
"""

from __future__ import annotations

from typing import Optional
import typer

# Import command functions
from .add import job as add_job
from .list import jobs as list_jobs_func
from .plan import job as plan_job
from .remove import job as remove_job
from .info import record_test as record_test_func
from .start import start_job, complete_job_id
from ..guard.check import check_guards
from ..guard.validate import validate_transition

# Create main job app
job_app = typer.Typer(name="job", help="Job management commands", no_args_is_help=True)


# Register direct commands (maintaining original CLI interface)
@job_app.command()
def add(src: str, name: str = "", paper: str = "A3"):
    """Add a new job to workspace."""
    return add_job(src, name, paper)


@job_app.command("list")
def list(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
):
    """List all jobs in workspace."""
    return list_jobs_func(json_output, csv_output)


@job_app.command()
def plan(
    job_id: str,
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job for plotting."""
    return plan_job(job_id, pen, interactive)


@job_app.command()
def remove(
    job_id: str,
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove a job from workspace."""
    return remove_job(job_id, force)


@job_app.command()
def start(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to start"
    ),
    preset: str = typer.Option(
        None, "--preset", "-p", help="Plot preset (fast, safe, preview, detail, draft)"
    ),
    port: Optional[str] = typer.Option(None, "--port", help="Device port"),
    model: int = typer.Option(1, "--model", help="Device model"),
):
    """Start plotting a job."""
    return start_job(job_id, preset, port, model)


@job_app.command()
def record_test(
    job_id: str,
    seconds: int = 5,
):
    """Record a test plot for timing."""
    return record_test_func(job_id, seconds)


@job_app.command()
def check():
    """Check system guards for job operations."""
    return check_guards()


@job_app.command()
def validate():
    """Validate job state transitions."""
    return validate_transition()
