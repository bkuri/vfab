"""
Recovery management commands for ploTTY CLI.

This module provides the main entry point for recovery commands,
delegating to specialized modules for different aspects of recovery.
"""

from __future__ import annotations

import typer

# Import specialized modules
from .listing import list_recoverable, job_status
from .operations import recover_job, recover_all_jobs_cmd, cleanup_journal
from ..core import get_available_job_ids

# Create recovery command group
recovery_app = typer.Typer(help="Crash recovery commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


# Listing commands
recovery_app.command("list")(list_recoverable)
recovery_app.command("status")(job_status)

# Operations commands
recovery_app.command()(recover_job)
recovery_app.command("recover-all")(recover_all_jobs_cmd)
recovery_app.command("cleanup")(cleanup_journal)
