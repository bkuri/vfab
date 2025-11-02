"""
Job management commands for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer

from ..config import load_config
from ..utils import error_handler, validate_file_exists
from .core import get_available_job_ids

# Create job command group
job_app = typer.Typer(help="Job management commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@job_app.command()
def add(src: str, name: str = "", paper: str = "A3"):
    """Add a new job to workspace."""
    try:
        cfg = load_config(None)

        # Validate source file exists
        src_path = Path(src)
        validate_file_exists(src_path, "Source SVG file")

        # TODO: Implement job addition logic
        print(f"Adding job from {src} with name '{name}' on paper {paper}")
    except Exception as e:
        error_handler.handle(e)


@job_app.command()
def plan(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plan"
    ),
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job for plotting."""
    try:
        # TODO: Implement job planning logic
        print(f"Planning job {job_id} with pen {pen}, interactive={interactive}")
    except Exception as e:
        error_handler.handle(e)


@job_app.command()
def record_test(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to record"
    ),
    seconds: int = 5,
):
    """Record a test plot for timing."""
    try:
        # TODO: Implement test recording logic
        print(f"Recording test for job {job_id} for {seconds} seconds")
    except Exception as e:
        error_handler.handle(e)
