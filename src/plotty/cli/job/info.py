"""
Job info and test commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

from ...utils import error_handler
from ..core import get_available_job_ids

info_app = typer.Typer(help="Job information and testing")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@info_app.command()
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
